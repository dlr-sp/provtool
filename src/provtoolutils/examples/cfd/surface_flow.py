#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1544, 802]

# destroy renderView1
Delete(renderView1)
del renderView1

# Create a new 'Line Chart View'
lineChartView1 = CreateView('XYChartView')
lineChartView1.ViewSize = [1544, 802]
lineChartView1.LeftAxisRangeMaximum = 6.66
lineChartView1.BottomAxisRangeMaximum = 6.66
lineChartView1.RightAxisRangeMaximum = 6.66
lineChartView1.TopAxisRangeMaximum = 6.66

# create a new 'XML Unstructured Grid Reader'
surface_flowvtu = XMLUnstructuredGridReader(FileName=['surface_flow.vtu'])
surface_flowvtu.PointArrayStatus = ['Density', 'Momentum', 'Energy', 'Pressure', 'Temperature', 'Mach', 'Pressure_Coefficient']

# set active source
SetActiveSource(surface_flowvtu)

# show data in view
surface_flowvtuDisplay = Show(surface_flowvtu, lineChartView1)
# trace defaults for the display properties.
surface_flowvtuDisplay.CompositeDataSetIndex = [0]
surface_flowvtuDisplay.XArrayName = 'Density'
surface_flowvtuDisplay.SeriesVisibility = ['Density', 'Energy', 'Mach', 'Momentum_Magnitude', 'Pressure', 'Pressure_Coefficient', 'Temperature']
surface_flowvtuDisplay.SeriesLabel = ['Density', 'Density', 'Energy', 'Energy', 'Mach', 'Mach', 'Momentum_X', 'Momentum_X', 'Momentum_Y', 'Momentum_Y', 'Momentum_Z', 'Momentum_Z', 'Momentum_Magnitude', 'Momentum_Magnitude', 'Pressure', 'Pressure', 'Pressure_Coefficient', 'Pressure_Coefficient', 'Temperature', 'Temperature', 'Points_X', 'Points_X', 'Points_Y', 'Points_Y', 'Points_Z', 'Points_Z', 'Points_Magnitude', 'Points_Magnitude']
surface_flowvtuDisplay.SeriesColor = ['Density', '0', '0', '0', 'Energy', '0.89', '0.1', '0.11', 'Mach', '0.22', '0.49', '0.72', 'Momentum_X', '0.3', '0.69', '0.29', 'Momentum_Y', '0.6', '0.31', '0.64', 'Momentum_Z', '1', '0.5', '0', 'Momentum_Magnitude', '0.65', '0.34', '0.16', 'Pressure', '0', '0', '0', 'Pressure_Coefficient', '0.89', '0.1', '0.11', 'Temperature', '0.22', '0.49', '0.72', 'Points_X', '0.3', '0.69', '0.29', 'Points_Y', '0.6', '0.31', '0.64', 'Points_Z', '1', '0.5', '0', 'Points_Magnitude', '0.65', '0.34', '0.16']
surface_flowvtuDisplay.SeriesPlotCorner = ['Density', '0', 'Energy', '0', 'Mach', '0', 'Momentum_X', '0', 'Momentum_Y', '0', 'Momentum_Z', '0', 'Momentum_Magnitude', '0', 'Pressure', '0', 'Pressure_Coefficient', '0', 'Temperature', '0', 'Points_X', '0', 'Points_Y', '0', 'Points_Z', '0', 'Points_Magnitude', '0']
surface_flowvtuDisplay.SeriesLabelPrefix = ''
surface_flowvtuDisplay.SeriesLineStyle = ['Density', '1', 'Energy', '1', 'Mach', '1', 'Momentum_X', '1', 'Momentum_Y', '1', 'Momentum_Z', '1', 'Momentum_Magnitude', '1', 'Pressure', '1', 'Pressure_Coefficient', '1', 'Temperature', '1', 'Points_X', '1', 'Points_Y', '1', 'Points_Z', '1', 'Points_Magnitude', '1']
surface_flowvtuDisplay.SeriesLineThickness = ['Density', '2', 'Energy', '2', 'Mach', '2', 'Momentum_X', '2', 'Momentum_Y', '2', 'Momentum_Z', '2', 'Momentum_Magnitude', '2', 'Pressure', '2', 'Pressure_Coefficient', '2', 'Temperature', '2', 'Points_X', '2', 'Points_Y', '2', 'Points_Z', '2', 'Points_Magnitude', '2']
surface_flowvtuDisplay.SeriesMarkerStyle = ['Density', '0', 'Energy', '0', 'Mach', '0', 'Momentum_X', '0', 'Momentum_Y', '0', 'Momentum_Z', '0', 'Momentum_Magnitude', '0', 'Pressure', '0', 'Pressure_Coefficient', '0', 'Temperature', '0', 'Points_X', '0', 'Points_Y', '0', 'Points_Z', '0', 'Points_Magnitude', '0']

# Properties modified on surface_flowvtuDisplay
surface_flowvtuDisplay.UseIndexForXAxis = 0

# Properties modified on surface_flowvtuDisplay
surface_flowvtuDisplay.XArrayName = 'Points_X'

# Properties modified on surface_flowvtu
surface_flowvtu.PointArrayStatus = ['Pressure_Coefficient']

# update the view to ensure updated data information
lineChartView1.Update()

# Properties modified on surface_flowvtuDisplay
surface_flowvtuDisplay.SeriesColor = ['Density', '0', '0', '0', 'Energy', '0.889998', '0.100008', '0.110002', 'Mach', '0.220005', '0.489998', '0.719997', 'Momentum_X', '0.300008', '0.689998', '0.289998', 'Momentum_Y', '0.6', '0.310002', '0.639994', 'Momentum_Z', '1', '0.500008', '0', 'Momentum_Magnitude', '0.650004', '0.340002', '0.160006', 'Pressure', '0', '0', '0', 'Pressure_Coefficient', '0.889998', '0.100008', '0.110002', 'Temperature', '0.220005', '0.489998', '0.719997', 'Points_X', '0.300008', '0.689998', '0.289998', 'Points_Y', '0.6', '0.310002', '0.639994', 'Points_Z', '1', '0.500008', '0', 'Points_Magnitude', '0.650004', '0.340002', '0.160006']
surface_flowvtuDisplay.SeriesPlotCorner = ['Density', '0', 'Energy', '0', 'Mach', '0', 'Momentum_Magnitude', '0', 'Momentum_X', '0', 'Momentum_Y', '0', 'Momentum_Z', '0', 'Points_Magnitude', '0', 'Points_X', '0', 'Points_Y', '0', 'Points_Z', '0', 'Pressure', '0', 'Pressure_Coefficient', '0', 'Temperature', '0']
surface_flowvtuDisplay.SeriesLineStyle = ['Density', '1', 'Energy', '1', 'Mach', '1', 'Momentum_Magnitude', '1', 'Momentum_X', '1', 'Momentum_Y', '1', 'Momentum_Z', '1', 'Points_Magnitude', '1', 'Points_X', '1', 'Points_Y', '1', 'Points_Z', '1', 'Pressure', '1', 'Pressure_Coefficient', '1', 'Temperature', '1']
surface_flowvtuDisplay.SeriesLineThickness = ['Density', '2', 'Energy', '2', 'Mach', '2', 'Momentum_Magnitude', '2', 'Momentum_X', '2', 'Momentum_Y', '2', 'Momentum_Z', '2', 'Points_Magnitude', '2', 'Points_X', '2', 'Points_Y', '2', 'Points_Z', '2', 'Pressure', '2', 'Pressure_Coefficient', '2', 'Temperature', '2']
surface_flowvtuDisplay.SeriesMarkerStyle = ['Density', '0', 'Energy', '0', 'Mach', '0', 'Momentum_Magnitude', '0', 'Momentum_X', '0', 'Momentum_Y', '0', 'Momentum_Z', '0', 'Points_Magnitude', '0', 'Points_X', '0', 'Points_Y', '0', 'Points_Z', '0', 'Pressure', '0', 'Pressure_Coefficient', '0', 'Temperature', '0']

# Properties modified on lineChartView1
lineChartView1.LeftAxisUseCustomRange = 1

# Properties modified on lineChartView1
lineChartView1.LeftAxisRangeMinimum = 2.0

# Properties modified on lineChartView1
lineChartView1.LeftAxisRangeMaximum = -2.0

# Properties modified on lineChartView1
lineChartView1.LeftAxisTitle = 'Cp'

# Properties modified on lineChartView1
lineChartView1.BottomAxisTitle = 'x/c'

# save screenshot
SaveScreenshot('../out/surface_flow.png', lineChartView1, ImageResolution=[1544, 802])

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
