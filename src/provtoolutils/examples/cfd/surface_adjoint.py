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
surface_adjointvtu = XMLUnstructuredGridReader(FileName=['surface_adjoint.vtu'])
surface_adjointvtu.PointArrayStatus = ['Adjoint_Density', 'Adjoint_Momentum', 'Adjoint_Energy', 'Sensitivity', 'Surface_Sensitivity']

# set active source
SetActiveSource(surface_adjointvtu)

# show data in view
surface_adjointvtuDisplay = Show(surface_adjointvtu, lineChartView1)
# trace defaults for the display properties.
surface_adjointvtuDisplay.CompositeDataSetIndex = [0]
surface_adjointvtuDisplay.XArrayName = 'Adjoint_Density'
surface_adjointvtuDisplay.SeriesVisibility = ['Adjoint_Density', 'Adjoint_Energy', 'Adjoint_Momentum_Magnitude', 'Sensitivity_Magnitude', 'Surface_Sensitivity']
surface_adjointvtuDisplay.SeriesLabel = ['Adjoint_Density', 'Adjoint_Density', 'Adjoint_Energy', 'Adjoint_Energy', 'Adjoint_Momentum_X', 'Adjoint_Momentum_X', 'Adjoint_Momentum_Y', 'Adjoint_Momentum_Y', 'Adjoint_Momentum_Z', 'Adjoint_Momentum_Z', 'Adjoint_Momentum_Magnitude', 'Adjoint_Momentum_Magnitude', 'Sensitivity_X', 'Sensitivity_X', 'Sensitivity_Y', 'Sensitivity_Y', 'Sensitivity_Z', 'Sensitivity_Z', 'Sensitivity_Magnitude', 'Sensitivity_Magnitude', 'Surface_Sensitivity', 'Surface_Sensitivity', 'Points_X', 'Points_X', 'Points_Y', 'Points_Y', 'Points_Z', 'Points_Z', 'Points_Magnitude', 'Points_Magnitude']
surface_adjointvtuDisplay.SeriesColor = ['Adjoint_Density', '0', '0', '0', 'Adjoint_Energy', '0.89', '0.1', '0.11', 'Adjoint_Momentum_X', '0.22', '0.49', '0.72', 'Adjoint_Momentum_Y', '0.3', '0.69', '0.29', 'Adjoint_Momentum_Z', '0.6', '0.31', '0.64', 'Adjoint_Momentum_Magnitude', '1', '0.5', '0', 'Sensitivity_X', '0.65', '0.34', '0.16', 'Sensitivity_Y', '0', '0', '0', 'Sensitivity_Z', '0.89', '0.1', '0.11', 'Sensitivity_Magnitude', '0.22', '0.49', '0.72', 'Surface_Sensitivity', '0.3', '0.69', '0.29', 'Points_X', '0.6', '0.31', '0.64', 'Points_Y', '1', '0.5', '0', 'Points_Z', '0.65', '0.34', '0.16', 'Points_Magnitude', '0', '0', '0']
surface_adjointvtuDisplay.SeriesPlotCorner = ['Adjoint_Density', '0', 'Adjoint_Energy', '0', 'Adjoint_Momentum_X', '0', 'Adjoint_Momentum_Y', '0', 'Adjoint_Momentum_Z', '0', 'Adjoint_Momentum_Magnitude', '0', 'Sensitivity_X', '0', 'Sensitivity_Y', '0', 'Sensitivity_Z', '0', 'Sensitivity_Magnitude', '0', 'Surface_Sensitivity', '0', 'Points_X', '0', 'Points_Y', '0', 'Points_Z', '0', 'Points_Magnitude', '0']
surface_adjointvtuDisplay.SeriesLabelPrefix = ''
surface_adjointvtuDisplay.SeriesLineStyle = ['Adjoint_Density', '1', 'Adjoint_Energy', '1', 'Adjoint_Momentum_X', '1', 'Adjoint_Momentum_Y', '1', 'Adjoint_Momentum_Z', '1', 'Adjoint_Momentum_Magnitude', '1', 'Sensitivity_X', '1', 'Sensitivity_Y', '1', 'Sensitivity_Z', '1', 'Sensitivity_Magnitude', '1', 'Surface_Sensitivity', '1', 'Points_X', '1', 'Points_Y', '1', 'Points_Z', '1', 'Points_Magnitude', '1']
surface_adjointvtuDisplay.SeriesLineThickness = ['Adjoint_Density', '2', 'Adjoint_Energy', '2', 'Adjoint_Momentum_X', '2', 'Adjoint_Momentum_Y', '2', 'Adjoint_Momentum_Z', '2', 'Adjoint_Momentum_Magnitude', '2', 'Sensitivity_X', '2', 'Sensitivity_Y', '2', 'Sensitivity_Z', '2', 'Sensitivity_Magnitude', '2', 'Surface_Sensitivity', '2', 'Points_X', '2', 'Points_Y', '2', 'Points_Z', '2', 'Points_Magnitude', '2']
surface_adjointvtuDisplay.SeriesMarkerStyle = ['Adjoint_Density', '0', 'Adjoint_Energy', '0', 'Adjoint_Momentum_X', '0', 'Adjoint_Momentum_Y', '0', 'Adjoint_Momentum_Z', '0', 'Adjoint_Momentum_Magnitude', '0', 'Sensitivity_X', '0', 'Sensitivity_Y', '0', 'Sensitivity_Z', '0', 'Sensitivity_Magnitude', '0', 'Surface_Sensitivity', '0', 'Points_X', '0', 'Points_Y', '0', 'Points_Z', '0', 'Points_Magnitude', '0']

# Properties modified on surface_adjointvtuDisplay
surface_adjointvtuDisplay.UseIndexForXAxis = 0

# Properties modified on surface_adjointvtuDisplay
surface_adjointvtuDisplay.XArrayName = 'Points_X'

# Properties modified on lineChartView1
lineChartView1.BottomAxisTitle = 'x/c'

# Properties modified on lineChartView1
lineChartView1.LeftAxisTitle = 'Sensitivity'

# save screenshot
SaveScreenshot('../out/surface_adjoint.png', lineChartView1, ImageResolution=[1544, 802])

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
