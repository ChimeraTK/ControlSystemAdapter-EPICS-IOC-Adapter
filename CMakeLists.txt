cmake_minimum_required(VERSION 3.16)

# Change project name, based on EPICS version
OPTION(EPICS_VERSION "Select major version of EPICS to build (3 or 7)")

if(NOT EPICS_VERSION)
  set(EPICS_VERSION "7")
endif()

if(EPICS_VERSION STREQUAL "3")
  project(ChimeraTK-ControlSystemAdapter-EPICS-IOC-Adapter)
elseif(EPICS_VERSION STREQUAL "7")
  project(ChimeraTK-ControlSystemAdapter-EPICS7-IOC-Adapter)
else()
  message(FATAL_ERROR "EPICS version must be defined! Please pass to cmake command line one of the following:\n"
    "-DEPICS_VERSION=3 to build against EPICS ver. 3.15\n"
    "-DEPICS_VERSION=7 to build against EPICS ver. 7.02")
endif()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake ${CMAKE_CURRENT_SOURCE_DIR}/cmake/Modules)

set(${PROJECT_NAME}_MAJOR_VERSION 02)
set(${PROJECT_NAME}_MINOR_VERSION 01)
set(${PROJECT_NAME}_PATCH_VERSION 01)
include(cmake/set_version_numbers.cmake)

find_package(ChimeraTK-ControlSystemAdapter 02.06 REQUIRED)
find_package(ChimeraTK-EPICS${EPICS_VERSION} REQUIRED)
get_target_property(EPICS_BASE ChimeraTK::EPICS${EPICS_VERSION} INTERFACE_EPICS_BASE)

find_package(readline REQUIRED)

# EPICS 7 requires the Yet Another JSON Library
if(EPICS_VERSION STREQUAL "7")
  find_package(libYajl REQUIRED)
endif()

find_program(PERL perl REQUIRED)

# set directory to gather all resulting libraries
set(PROJECT_LIB_DIR ${PROJECT_BINARY_DIR}/lib)

configure_file(adapter/CONFIG_SITE.local.in ${PROJECT_BINARY_DIR}/adapterCONFIG_SITE.local)
configure_file(adapter/RELEASE.local.in ${PROJECT_BINARY_DIR}/adapterRELEASE.local)

# configure files required to build the IOC with the  ControlSystemAdapter-EPICS as device support
configure_file(ioc/RELEASE.in ${PROJECT_BINARY_DIR}/iocRELEASE)
configure_file(ioc/epics${EPICS_VERSION}_iocSrcMakefile.in ${PROJECT_BINARY_DIR}/iocSrcMakefile)
configure_file(ioc/CONFIG_SITE.in ${PROJECT_BINARY_DIR}/iocCONFIG_SITE)

# build the ControlSystemAdapter-EPICS
add_custom_target(${PROJECT_NAME}-adapter ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildAdapter ${CMAKE_CURRENT_SOURCE_DIR}/ChimeraTK-ControlSystemAdapter-EPICS ${ChimeraTK-ControlSystemAdapter_PREFIX} ${EPICS_BASE}
  WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
  BYPRODUCTS ${PROJECT_LIB_DIR}/libChimeraTK-ControlSystemAdapter-EPICS.a)

# generate the IOC sources
set(iocSources ${PROJECT_BINARY_DIR}/src/ChimeraTKMain.cpp ${PROJECT_BINARY_DIR}/src/ChimeraTK_registerRecordDeviceDriver.cpp)
add_custom_target(${PROJECT_NAME}-ioc ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildIoc ${EPICS_BASE}
  WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
  DEPENDS ${PROJECT_NAME}-adapter
  BYPRODUCTS ${iocSources})

# define the library
add_library(${PROJECT_NAME} SHARED ${iocSources})
add_dependencies(${PROJECT_NAME} ${PROJECT_NAME}-ioc)

target_link_libraries(${PROJECT_NAME} PRIVATE ChimeraTK::EPICS${EPICS_VERSION})
target_link_libraries(${PROJECT_NAME} PRIVATE ChimeraTK::ChimeraTK-ControlSystemAdapter)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_LIB_DIR}/libChimeraTK-ControlSystemAdapter-EPICS.a)

set_target_properties(${PROJECT_NAME} PROPERTIES VERSION ${${PROJECT_NAME}_FULL_LIBRARY_VERSION} SOVERSION ${${PROJECT_NAME}_SOVERSION})

set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "-Wl,--no-undefined -Wl,--no-as-needed")

# do not remove runtime path of the library when installing
set_property(TARGET ${PROJECT_NAME} PROPERTY INSTALL_RPATH_USE_LINK_PATH TRUE)

# Install the library and a template directory structure for IOCs
include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}Targets LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(FILES ${PROJECT_BINARY_DIR}/ioc/dbd/ChimeraTK.dbd DESTINATION share/${PROJECT_NAME}/iocTemplate/dbd)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/iocTemplate/iocBoot/iocChimeraTKApp/st.cmd DESTINATION share/${PROJECT_NAME}/iocTemplate/iocBoot/iocChimeraTKApp)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/iocTemplate/db/readme.txt DESTINATION share/${PROJECT_NAME}/iocTemplate/db)

set(PROVIDES_EXPORTED_TARGETS 1)
list(APPEND ${PROJECT_NAME}_PUBLIC_DEPENDENCIES)
include(${CMAKE_SOURCE_DIR}/cmake/create_cmake_config_files.cmake)
