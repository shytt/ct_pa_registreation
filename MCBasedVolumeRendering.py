#!/usr/bin/env python

"""
"""

import vtk
import numpy
import argparse
from vtk.util.vtkImageImportFromArray import *
import scipy.io as scio
from skimage.transform import rescale, resize, downscale_local_mean
import h5py

def get_program_parameters():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--CT", action="store_true", help="generate CT surface")
    parser.add_argument("--US", action="store_true", help="generate US surface")
    parser.add_argument("-f", "--filename", help="the volume data location. For CT, .vol data is used and for US, .mat data is used.")
    parser.add_argument("-v", "--isovalue", type=float, default = 0, help="the iso value for the surface")
    parser.add_argument("-s", "--savename", help="save the corresponding file as pointcloud file .ply")
    parser.add_argument("-c", "--colorsurf",type = int, nargs=4, default = [255, 125, 64, 255], help="the color of surface")
    parser.add_argument("-b", "--colorbkg",type = int, nargs=4, default = [51, 77, 102, 255], help="the color of background")
    parser.add_argument("-r", "--resize",type = float, default = 1, help="resize the surface by a multiplyer")
    parser.add_argument("--np", action="store_true", help="do not plot the surface in vtk")
    # iso-surface related, signal source related, resolution, step size
    args = parser.parse_args()
    return args

def main():
    args = get_program_parameters()

    # create the color table
    colors = vtk.vtkNamedColors()
    colors.SetColor("surfColor", args.colorsurf)
    colors.SetColor("BkgColor", args.colorbkg)

    # Create the renderer, the render window, and the interactor. The renderer
    # draws into the render window, the interactor enables mouse- and
    # keyboard-based interaction with the data within the render window.
    #
    aRenderer = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(aRenderer)

    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    if not args.filename:
        print("Must input a volume data to read!")
        return 

    if args.CT:
        volArray = numpy.fromfile(args.filename,dtype=numpy.dtype('float32'))
        volArray = volArray.reshape((974,999,798))
        volArray = rescale(volArray, args.resize, anti_aliasing=True)
    elif args.US:
        volArray = h5py.File(args.filename,'r')
        volArray = numpy.asarray(volArray['usMasked'], order='C')
    else:
        print("Must choose CT or US!") 
        return   

    importer = vtkImageImportFromArray()
    importer.SetArray(volArray)
    importer.Update() 
    print("Finish loading data.")

    # An isosurface, or contour value of 500 is known to correspond to the
    # skin of the patient.
    Extractor = vtk.vtkMarchingCubes()
    Extractor.SetInputConnection(importer.GetOutputPort())
    Extractor.SetValue(0, args.isovalue)
    
    if args.savename:
        plyWriter = vtk.vtkPLYWriter()
        plyWriter.SetFileName(args.savename)
        plyWriter.SetInputConnection(Extractor.GetOutputPort())
        plyWriter.Write()
        
    if args.np:
        return

    print("Start rendering.")
    Mapper = vtk.vtkPolyDataMapper()
    Mapper.SetInputConnection(Extractor.GetOutputPort())
    Mapper.ScalarVisibilityOff()

    surf = vtk.vtkActor()
    surf.SetMapper(Mapper)
    surf.GetProperty().SetDiffuseColor(colors.GetColor3d("surfColor"))

    # An outline provides context around the data.
    #
    outlineData = vtk.vtkOutlineFilter()
    outlineData.SetInputConnection(importer.GetOutputPort())

    mapOutline = vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outlineData.GetOutputPort())

    outline = vtk.vtkActor()
    outline.SetMapper(mapOutline)
    outline.GetProperty().SetColor(colors.GetColor3d("Black"))


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
    aRenderer.AddActor(surf)
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





if __name__ == '__main__':
    main()
