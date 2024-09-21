import ctypes
from ctypes import windll, c_int, c_char, byref, c_long, \
    pointer, c_float, c_char_p, cdll

import sys
import platform

from pathlib import Path
from spectrograph import ATSpectrograph

try:
    # Check operating system and load library
    if platform.system() == "Linux":
        dllpath = Path("/usr/local/lib/libandor.so")
        _dll = cdll.LoadLibrary(str(dllpath))
    elif platform.system() == "Windows":
        dllpath = Path('C:\\Program Files\\Andor SDK')
        if platform.machine() == "AMD64": 
            dllpath = dllpath.joinpath("pyAndorSpectrograph/atspectrograph.dll")
        else:
            dllpath = dllpath.joinpath("Shamrock/ShamrockCIF.dll") #check if this line is running
        _dll = windll.LoadLibrary(str(dllpath))

except Exception as e:
    raise Exception(f'Could not import Kymera library: {str(e)}')


class KymeraSDK:
    """
    Andor class which is meant to provide the Python version of the same
    functions that are defined in the Andor's SDK.
    """
    def __init__(self):
        '''
        'C:\\Program Files\\Andor SDK'
        
        Loads and initializes the hardware driver.
        Initializes local parameters

        Input:
            dllpath (string)   : The path where to find the sdk2 dlls
            control type (string) : either "camera", "shamrock" or "both". to be set to initialize all or part of the libraries
        '''

        print("Initializing Kymera...", )
        _dll = ATSpectrograph()
        error = _dll.Initialize()

        nodevices = c_int()
        error = _dll.GetNumberDevices(byref(nodevices))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        print(f'(Nr of devices: {nodevices.value})')
        
        # Initiate parameters - Shamrock
        self.NrPixels = 0

    def __del__(self):
        error = _dll.Close()
        if error != 20202:
            raise IOError(ERROR_CODE[error])

    def close(self):
        error = _dll.Close()
        if error != 20202:
            raise IOError(ERROR_CODE[error])

    def GetNumberDevicesSR(self):
        nodevices = c_int()
        error = _dll.GetNumberDevices(byref(nodevices))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], nodevices.value

    def GetFunctionReturnDescriptionSR(self, error, MaxDescStrLen):
        error = c_int(error)
        MaxDescStrLen = c_int(MaxDescStrLen)
        description = c_char_p()
        error = _dll.GetFunctionReturnDescription(error, description, MaxDescStrLen)
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], description.value

    #---- sdkeeprom functions

    def GetSerialNumberSR(self, device):
        device = c_int(device)
        serial = ctypes.create_string_buffer(128)
        error = _dll.GetSerialNumber(device, byref(serial))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], serial.value

    def EepromGetOpticalParamsSR(self, device):
        device = c_int(device)
        FocalLength = c_float()
        AngularDeviation = c_float()
        FocalTilt = c_float()
        error = _dll.EepromGetOpticalParams(device, byref(FocalLength),
                                                    byref(AngularDeviation), byref(FocalTilt)) #check this is the command is correct
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], FocalLength.value, AngularDeviation.value, FocalTilt.value

    #---- sdkgrating functions
    def SetGratingSR(self, device, grating):
        device = c_int(device)
        grating = c_int(grating)
        error = _dll.SetGrating(device, grating)
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error]

    def GetGratingSR(self, device):
        device = c_int(device)
        grating = c_int()
        error = _dll.GetGrating(device, byref(grating))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], grating.value

    def WavelengthResetSR(self, device):
        device = c_int(device)
        error = _dll.WavelengthReset(device)
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error]

    def GetNumberGratingsSR(self, device):
        device = c_int(device)
        noGratings = c_int()
        error = _dll.GetNumberGratings(device, byref(noGratings))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], noGratings.value

    def GetGratingInfoSR(self, device, grating):
        device = c_int(device)
        grating = c_int(grating)
        Lines = c_float()
        Blaze = ctypes.create_string_buffer(128)
        Home = c_int()
        Offset = c_int()
        error = _dll.GetGratingInfo(device, grating, 
                    byref(Lines), byref(Blaze), byref(Home), byref(Offset))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], Lines.value, Blaze.value.decode(), Home.value, Offset.value
    
    #---- sdkwavelength functions
    def SetWavelengthSR(self, device, wavelength):
        device = c_int(device)
        wavelength = c_float(wavelength)
        error = _dll.SetWavelength(device, wavelength)
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error]
    
    def GetWavelengthSR(self, device):
        device = c_int(device)
        wavelength = c_float()
        error = _dll.GetWavelength(device, byref(wavelength))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], wavelength.value
    
    def GetWavelengthLimitsSR(self, device, grating):
        device = c_int(device)
        grating = c_int(grating)
        minLambda = c_float()
        maxLambda = c_float()
        error = _dll.GetWavelengthLimits(device, grating, byref(minLambda), byref(maxLambda))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], minLambda.value, maxLambda.value
    
    def GotoZeroOrderSR(self, device):
        device = c_int(device)
        error = _dll.GotoZeroOrder(device)
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error]
    
    def AtZeroOrderSR(self, device):
        device = c_int(device)
        atZeroOrder = c_int()
        error = _dll.AtZeroOrder(device, byref(atZeroOrder))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], atZeroOrder.value
    
    #---- sdkcalibration functions
    def SetNumberPixelsSR(self, device, NumberPixels):
        device = c_int(device)
        NumberPixels = c_int(NumberPixels)
        error = _dll.SetNumberPixels(device, NumberPixels)
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        self.NrPixels = NumberPixels.value
        return ERROR_CODE[error]
    
    def SetPixelWidthSR(self, device, Width):
        device = c_int(device)
        Width = c_float(Width)
        error = _dll.SetPixelWidth(device, Width)
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error]
    
    def GetNumberPixelsSR(self, device):
        device = c_int(device)
        NumberPixels = c_int()
        error = _dll.GetNumberPixels(device, byref(NumberPixels))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        self.NrPixels = NumberPixels.value
        return ERROR_CODE[error], NumberPixels.value
    
    def GetPixelWidthSR(self, device):
        device = c_int(device)
        Width = c_float()
        error = _dll.GetPixelWidth(device, byref(Width))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], Width.value
    
    def GetCalibrationSR(self, device, Npxls):
        device = c_int(device)
        CalibrationValues = (c_float*int(Npxls))()
        error = _dll.GetCalibration(device, byref(CalibrationValues), int(Npxls))
        if error != 20202:
            raise IOError(ERROR_CODE[error])
        return ERROR_CODE[error], CalibrationValues[:]


# ####################################################

# List of error codes
ERROR_CODE = {

    20201: "KYMERA_COMMUNICATION_ERROR",
    20202: "KYMERA_SUCCESS",
    20266: "KYMERA_P1INVALID",
    20267: "KYMERA_P2INVALID",
    20268: "KYMERA_P3INVALID",
    20269: "KYMERA_P4INVALID",
    20270: "KYMERA_P5INVALID",
    20275: "KYMERA_NOT_INITIALIZED",
    20292: "KYMERA_NOT_AVAILABLE"
}


