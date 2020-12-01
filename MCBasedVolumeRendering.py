#!/usr/bin/env python

"""
"""

import vtk
import numpy
from vtk.util.vtkImageImportFromArray import *
import scipy.io as scio


def main():
    colors = vtk.vtkNamedColors()



    #fileName = get_program_parameters()
    colors.SetColor("CTColor", [255, 125, 64, 255])
    colors.SetColor("BkgColor", [51, 77, 102, 255])
    colors.SetColor("USColor", [255, 255, 0, 125])

    # Create the renderer, the render window, and the interactor. The renderer
    # draws into the render window, the interactor enables mouse- and
    # keyboard-based interaction with the data within the render window.
    #
    aRenderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(aRenderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    '''
    reader = vtk.vtkTIFFReader()
    reader.SetFilePrefix(filename)
    reader.SetFilePattern("%s%05d.tif")
    reader.SetDataExtent(0,999,0,999,1,1001)
    reader.SetDataSpacing(1,1,0.001)
    reader.Update()
    '''

    volPath = "20201121_GF_2/20201121_GF_2/20201121.vol"
    volArray = numpy.fromfile(volPath,dtype=numpy.dtype('float32'))
    volArray = volArray.reshape((896,777,996))
    #print(volArray.shape)
    importer = vtkImageImportFromArray()
    importer.SetArray(volArray)
    importer.Update() 


    # An isosurface, or contour value of 500 is known to correspond to the
    # skin of the patient.
    CTExtractor = vtk.vtkMarchingCubes()
    CTExtractor.SetInputConnection(importer.GetOutputPort())
    CTExtractor.SetValue(0, 0.0775)
    
    

    CTname = "CT.ply"
    plyWriter = vtk.vtkPLYWriter()
    plyWriter.SetFileName(CTname)
    plyWriter.SetInputConnection(CTExtractor.GetOutputPort())
    plyWriter.Write()


    CTMapper = vtk.vtkPolyDataMapper()
    CTMapper.SetInputConnection(CTExtractor.GetOutputPort())
    CTMapper.ScalarVisibilityOff()

    CT = vtk.vtkActor()
    CT.SetMapper(CTMapper)
    CT.GetProperty().SetDiffuseColor(colors.GetColor3d("CTColor"))

    # An outline provides context around the data.
    #
    outlineData = vtk.vtkOutlineFilter()
    outlineData.SetInputConnection(importer.GetOutputPort())

    mapOutline = vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outlineData.GetOutputPort())

    outline = vtk.vtkActor()
    outline.SetMapper(mapOutline)
    outline.GetProperty().SetColor(colors.GetColor3d("Black"))

    volPath = "volume.mat"


    '''f = h5py.File(volPath,'r')
    data = f.get('data/variable1')
    data = np.array(data)'''
    USvolArray = scio.loadmat(volPath)
    USvolArray = numpy.asarray(USvolArray['usData'], order='C')
    USimporter = vtkImageImportFromArray()
    USimporter.SetArray(USvolArray)
    USimporter.Update() 


    # An isosurface, or contour value of 500 is known to correspond to the
    # skin of the patient.
    USExtractor = vtk.vtkMarchingCubes()
    USExtractor.SetInputConnection(USimporter.GetOutputPort())
    USExtractor.SetValue(0, 20)

    USname = "US.ply"
    plyWriter = vtk.vtkPLYWriter()
    plyWriter.SetFileName(USname)
    plyWriter.SetInputConnection(USExtractor.GetOutputPort())
    plyWriter.Write()

    USMapper = vtk.vtkPolyDataMapper()
    USMapper.SetInputConnection(USExtractor.GetOutputPort())
    USMapper.ScalarVisibilityOff()

    US = vtk.vtkActor()
    US.SetMapper(USMapper)
    US.GetProperty().SetDiffuseColor(colors.GetColor3d("USColor"))

    # An outline provides context around the data.
    #
    USoutlineData = vtk.vtkOutlineFilter()
    USoutlineData.SetInputConnection(USimporter.GetOutputPort())

    USmapOutline = vtk.vtkPolyDataMapper()
    USmapOutline.SetInputConnection(USoutlineData.GetOutputPort())

    USoutline = vtk.vtkActor()
    USoutline.SetMapper(USmapOutline)
    USoutline.GetProperty().SetColor(colors.GetColor3d("Black"))

    # It is convenient to create an initial view of the data. The FocalPoint
    # and Position form a vector direction. Later on (ResetCamera() method)
    # this vector is used to position the camera to look at the data in
    # this direction.
    aCamera = vtk.vtkCamera()
    aCamera.SetViewUp(0, 0, -1)
    aCamera.SetPosition(0, -1, 0)
    aCamera.SetFocalPoint(0, 0, 0)
    aCamera.ComputeViewPlaneNormal()
    aCamera.Azimuth(30.0)
    aCamera.Elevation(30.0)

    # Actors are added to the renderer. An initial camera view is created.
    # The Dolly() method moves the camera towards the FocalPoint,
    # thereby enlarging the image.
    aRenderer.AddActor(outline)
    aRenderer.AddActor(CT)
    aRenderer.AddActor(USoutline)
    aRenderer.AddActor(US)
    aRenderer.SetActiveCamera(aCamera)
    aRenderer.ResetCamera()
    aCamera.Dolly(1.5)

    # Set a background color for the renderer and set the size of the
    # render window (expressed in pixels).
    aRenderer.SetBackground(colors.GetColor3d("BkgColor"))
    renWin.SetSize(640, 480)

    # Note that when camera movement occurs (as it does in the Dolly()
    # method), the clipping planes often need adjusting. Clipping planes
    # consist of two planes: near and far along the view direction. The
    # near plane clips out objects in front of the plane the far plane
    # clips out objects behind the plane. This way only what is drawn
    # between the planes is actually rendered.
    aRenderer.ResetCameraClippingRange()

    # Initialize the event loop and then start it.
    iren.Initialize()
    iren.Start()


def get_program_parameters():
    import argparse
    description = 'The skin extracted from a CT dataset of the head.'
    epilogue = '''
    Derived from VTK/Examples/Cxx/Medical1.cxx
    This example reads a volume dataset, extracts an isosurface that
     represents the skin and displays it.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='FullHead.mhd.')
    args = parser.parse_args()
    return args.filename


if __name__ == '__main__':
    main()
