# Regional Map Functions
def regionalMap(tables, variabels, dt1, dt2, lat1, lat2, lon1, lon2, depth1, depth2, fname, exportDataFlag):
    for i in tqdm(range(len(tables)), desc='overall'):
        
        unit = tables[i].variables[variables[i]].attrs['units']
        
        toDateTime = tables[i].indexes['TIME'].to_datetimeindex()
        tables[i]['TIME'] = toDateTime
        table = tables[i].sel(TIME = slice(startDate, endDate), LAT_C = slice(lat1, lat2), LON_C = slice(lon1, lon2), DEP_C = slice(depth1, depth2))
        
        varData = table.variables[variables[i]][0,0,:,:].values       
        
        lats = table.variables['LAT_C'].values.tolist()
        lons = table.variables['LON_C'].values.tolist()
        
        shape = (len(lats), len(lons))
        
        varData.reshape(shape)

        varData[varData < 0] = float('NaN')
        varData = [np.asarray(varData)]
        lats = [np.asarray(lats)]
        lons = [np.asarray(lons)]
        
        bokehMap(varData, unit, 'regional', lats, lons, unit, 'OTHER', variables[i])

def bokehMap(data, subject, fname, lat, lon, units, tables, variabels):
    TOOLS="crosshair,pan,zoom_in,wheel_zoom,zoom_out,box_zoom,reset,save,"
    p = []
    for ind in range(len(data)):

        w, h = com.canvasRect(dw=np.max(lon[ind])-np.min(lon[ind]), dh=np.max(lat[ind])-np.min(lat[ind]))
        p1 = figure(tools=TOOLS, toolbar_location="right", title=subject[ind], plot_width=w, plot_height=h, x_range=(np.min(lon[ind]), np.max(lon[ind])), y_range=(np.min(lat[ind]), np.max(lat[ind])))
        p1.xaxis.axis_label = 'Longitude'
        p1.yaxis.axis_label = 'Latitude'
    
        unit = units
        
        bounds = com.getBounds(variabels[ind])
        
        paletteName = com.getPalette(variabels[ind])
        low, high = bounds[0], bounds[1]
        
        if low == None:
            low, high = np.nanmin(data[ind].flatten()), np.nanmax(data[ind].flatten())
        color_mapper = LinearColorMapper(palette=paletteName, low=low, high=high)
        p1.image(image=[data[ind]], color_mapper=color_mapper, x=np.min(lon[ind]), y=np.min(lat[ind]), dw=np.max(lon[ind])-np.min(lon[ind]), dh=np.max(lat[ind])-np.min(lat[ind]))
        p1.add_tools(HoverTool(
            tooltips=[
                ('longitude', '$x'),
                ('latitude', '$y'),
                (variabels[ind]+unit, '@image'),
            ],
            mode='mouse'
        ))
        color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(),
                        label_standoff=12, border_line_color=None, location=(0,0))
        p1.add_layout(color_bar, 'right')
        p.append(p1)
    if len(p) > 0:
       # if not inline:      ## if jupyter is not the caller
       #     dirPath = 'embed/'
       #     if not os.path.exists(dirPath):
       #         os.makedirs(dirPath)        
       #     output_file(dirPath + fname + ".html", title="Regional Map")
        show(column(p))
    return


# Sectional Map Functions
def regulate(lat, lon, depth, data):
    depth = -1* depth 
    deltaZ = np.min( np.abs( depth - np.roll(depth, -1) ) )
    newDepth =  np.arange(np.min(depth), np.max(depth), deltaZ)        

    if len(lon) > len(lat):
        lon1, depth1 = np.meshgrid(lon, depth)
        lon2, depth2 = np.meshgrid(lon, newDepth)
        lon1 = lon1.ravel()
        lon1 = list(lon1[lon1 != np.isnan])
        depth1 = depth1.ravel()
        depth1 = list(depth1[depth1 != np.isnan])
        data = data.ravel()
        data = list(data[data != np.isnan])
        data = griddata((lon1, depth1), data, (lon2, depth2), method='linear')
    else:   
        lat1, depth1 = np.meshgrid(lat, depth)
        lat2, depth2 = np.meshgrid(lat, newDepth)
        lat1 = lat1.ravel()
        lat1 = list(lat1[lat1 != np.isnan])
        depth1 = depth1.ravel()
        depth1 = list(depth1[depth1 != np.isnan])
        data = data.ravel()
        data = list(data[data != np.isnan])
        data = griddata((lat1, depth1), data, (lat2, depth2), method='linear')

    depth = -1* depth 
    return data

def bokehSec(data, subject, fname, ys, xs, zs, units, variabels):
    TOOLS="crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"
    w = 1000
    h = 500
    p = []
    data_org = list(data)
    for ind in range(len(data_org)):
        data = data_org[ind]
        lon = xs[ind]
        lat = ys[ind]
        depth = zs[ind]      
        
        bounds = (None, None)
        paletteName = com.getPalette(variabels[ind], 10)
        low, high = bounds[0], bounds[1]
        
        if low == None:
            low, high = np.nanmin(data[ind].flatten()), np.nanmax(data[ind].flatten())
        color_mapper = LinearColorMapper(palette=paletteName, low=low, high=high)
        output_notebook()
        if len(lon) > len(lat):
            p1 = figure(tools=TOOLS, toolbar_location="above", title=subject[ind], plot_width=w, plot_height=h, x_range=(np.min(lon), np.max(lon)), y_range=(-np.max(depth), -np.min(depth)))
            data = np.nanmean(data, axis=0)
            data = np.transpose(data)
            data = np.squeeze(data)
            xLabel = 'Longitude'
            data = regulate(lat, lon, depth, data)
            p1.image(image=[data], color_mapper=color_mapper, x=np.min(lon), y=-np.max(depth), dw=np.max(lon)-np.min(lon), dh=np.max(depth)-np.min(depth))
        else:
            p1 = figure(tools=TOOLS, toolbar_location="above", title=subject[ind], plot_width=w, plot_height=h, x_range=(np.min(lat), np.max(lat)), y_range=(-np.max(depth), -np.min(depth)))
            data = np.nanmean(data, axis=1)
            data = np.transpose(data)
            data = np.squeeze(data)
            xLabel = 'Latitude'      
            data = regulate(lat, lon, depth, data)
            p1.image(image=[data], color_mapper=color_mapper, x=np.min(lat), y=-np.max(depth), dw=np.max(lat)-np.min(lat), dh=np.max(depth)-np.min(depth))

        p1.xaxis.axis_label = xLabel
        p1.add_tools(HoverTool(
            tooltips=[
                (xLabel.lower(), '$x'),
                ('depth', '$y'),
                (variabels[ind]+units[ind], '@image'),
            ],
            mode='mouse'
        ))

        p1.yaxis.axis_label = 'depth [m]'
        color_bar = ColorBar(color_mapper=color_mapper, ticker=BasicTicker(),
                        label_standoff=12, border_line_color=None, location=(0,0))
        p1.add_layout(color_bar, 'right')
        p.append(p1)
    dirPath = 'embed/'
   # if not os.path.exists(dirPath):
   #     os.makedirs(dirPath)        
   # if not inline:      ## if jupyter is not the caller
   # output_file(dirPath + fname + ".html", title="Section Map")
    show(column(p))
    return

def xarraySectionMap(tables, variabels, dt1, dt2, lat1, lat2, lon1, lon2, depth1, depth2, fname, exportDataFlag):
    data, lats, lons, subs, frameVars, units = [], [], [], [], [], []
    xs, ys, zs = [], [], []
    for i in tqdm(range(len(tables)), desc='overall'):
        
        toDateTime = tables[i].indexes['TIME'].to_datetimeindex()
        tables[i]['TIME'] = toDateTime
        table = tables[i].sel(TIME = slice(dt1, dt2), LAT_C = slice(lat1, lat2), LON_C = slice(lon1, lon2), DEP_C = slice(depth1, depth2))
        ############### export retrieved data ###############
        if exportDataFlag:      # export data
            dirPath = 'data/'
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)                
            exportData(df, path=dirPath + fname + '_' + tables[i] + '_' + variabels[i] + '.csv')
        #####################################################

        times = np.unique(table.variables['TIME'].values)
        lats = np.unique(table.variables['LAT_C'].values)
        lons = np.unique(table.variables['LON_C'].values)
        depths = np.flip(np.unique(table.variables['DEP_C'].values))
        shape = (len(lats), len(lons), len(depths))
        
        hours = [None]

        unit = '[PLACEHOLDER]'

        for t in times:
            for h in hours:
                frame = table.sel(TIME = t, method = 'nearest')
                sub = variabels[i] + unit + ', TIME: ' + str(t) 
                if h != None:
                    frame = frame[frame['hour'] == h]
                    sub = sub + ', hour: ' + str(h) + 'hr'
                try:    
                    shot = frame[variabels[i]].values.reshape(shape)
                    shot[shot < 0] = float('NaN')
                except Exception as e:
                    continue    
                data.append(shot)
                
                xs.append(lons)
                ys.append(lats)
                zs.append(depths)

                frameVars.append(variabels[i])
                units.append(unit)
                subs.append(sub)
    
    bokehSec(data=data, subject=subs, fname=fname, ys=ys, xs=xs, zs=zs, units=units, variabels=frameVars)
    return

# Histogram Function
def xarrayPlotDist(tables, variables, startDate, endDate, lat1, lat2, lon1, lon2, depth1, depth2, fname, exportDataFlag, marker='-', msize=30, clr='purple'):
    p = []
    lw = 2
    w = 800
    h = 400
    TOOLS = 'pan,wheel_zoom,zoom_in,zoom_out,box_zoom, undo,redo,reset,tap,save,box_select,poly_select,lasso_select'
    for i in tqdm(range(len(tables)), desc='overall'):
        
        unit = tables[i].variables[variables[i]].attrs['units']
        
        varData = tables[i].sel(TIME = slice(startDate, endDate), LAT_C = slice(lat1, lat2), LON_C = slice(lon1, lon2), DEP_C = slice(depth1, depth2))
        varData = varData.variables[variables[i]][:].values
        varData[varData < 0] = float('NaN')
        
        varData = varData.tolist()[0][0]
        elems = []
        for list in varData:
            for item in list:
                elems.append(item)
        varData = pd.Series(elems).dropna()

        if exportDataFlag:
            exportData(y, tables[i], variables[i], startDate, endDate, lat1, lat2, lon1, lon2, depth1, depth2)
        try:    
            carData = varData[~np.isnan(varData)]     # remove nans
        except Exception as e:
            continue   
            
        hist, edges = np.histogram(varData, density=True, bins=50)
        
        output_notebook()
        
        p1 = figure(tools=TOOLS, toolbar_location="above", plot_width=w, plot_height=h)
        p1.yaxis.axis_label = 'Density'
        p1.xaxis.axis_label = variables[i] + ' (' +str(unit) + ')'
        leg = variables[i]
        fill_alpha = 0.4   
        cr = p1.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], fill_color="dodgerblue", line_color=None, hover_fill_color="firebrick", fill_alpha=fill_alpha, hover_alpha=0.7, hover_line_color="white", legend=leg)
        p1.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='mouse'))
        p.append(p1)
    dirPath = 'embed/'
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)        
    
    #if not inline:      ## if jupyter is not the caller
    #    output_file(dirPath + fname + ".html", title="Histogram")
    #    print('test')
    show(column(p))
    return

# Time Series Function
def plotTSX(tables, variables, startDate, endDate, lat1, lat2, lon1, lon2, depth1, depth2, fname, exportDataFlag, marker='-', msize=20, clr='purple'):
    p = []
    lw = 2
    w = 800
    h = 400
    TOOLS = 'pan,wheel_zoom,zoom_in,zoom_out,box_zoom, undo,redo,reset,tap,save,box_select,poly_select,lasso_select'
    for i in tqdm(range(len(tables)), desc='overall'):
        dt = 1     
        unit = tables[i].variables[variables[i]].attrs['units']
        
        toDateTime = tables[i].indexes['TIME'].to_datetimeindex()
        tables[i]['TIME'] = toDateTime
        y = tables[i].sel(TIME = slice(startDate, endDate), LAT_C = slice(lat1, lat2), LON_C = slice(lon1, lon2), DEP_C = slice(depth1, depth2))
        t = y.variables['TIME'].values
        y = y.variables[variables[i]][:,0,0,0].values.tolist()
        
        if exportDataFlag:
            exportData(t, y, yErr, tables[i], variables[i], lat1, lat2, lon1, lon2, depth1, depth2)
        
        output_notebook()
        p1 = figure(tools=TOOLS, toolbar_location="above", plot_width=w, plot_height=h)
        p1.xaxis.axis_label = 'Time'        
        p1.yaxis.axis_label = variables[i] + str(unit)
        leg = variables[i]
        fill_alpha = 0.3        
        cr = p1.circle(t, y, fill_color="grey", hover_fill_color="firebrick", fill_alpha=fill_alpha, hover_alpha=0.3, line_color=None, hover_line_color="white", legend=leg, size=msize)
        p1.line(t, y, line_color=clr, line_width=lw, legend=leg)
        p1.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))
        
        
        p1.xaxis.formatter=DatetimeTickFormatter(
                hours=["%d %B %Y"],
                days=["%d %B %Y"],
                months=["%d %B %Y"],
                years=["%d %B %Y"],
            )
        p1.xaxis.major_label_orientation = pi/4

        p.append(p1)
    dirPath = 'embed/'
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)        
    #if not inline:      ## if jupyter is not the caller
    #   output_file(dirPath + fname + ".html", title="TimeSeries")
    show(column(p))
    return