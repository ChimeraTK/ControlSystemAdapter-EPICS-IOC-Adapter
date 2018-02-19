#!<ApplicationExecutable>

## Register all support components
dbLoadDatabase("../../dbd/ChimeraTK.dbd",0,0)
ChimeraTK_registerRecordDeviceDriver(pdbbase)

## Setup ChimeraTKApp application and set polling intervall to 100us
chimeraTKConfigureApplication("ChimeraTKApp", 100)

## Load record instances
dbLoadRecords("../../db/<ApplicationName>.db","P=<InstanceName>,APP=ChimeraTKApp")

## Initialise the IOC
iocInit()

## Start any sequence programs
#seq sncllrfctrl,"user=<user>"
