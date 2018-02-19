PROJECT(ChimeraTK-ControlSystemAdapter-EPICSIOCAdapter)
cmake_minimum_required(VERSION 2.8)

include(cmake/add_dependency.cmake)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake ${CMAKE_CURRENT_SOURCE_DIR}/cmake/Modules)

set(${PROJECT_NAME}_MAJOR_VERSION 00)
set(${PROJECT_NAME}_MINOR_VERSION 00)
set(${PROJECT_NAME}_PATCH_VERSION 00)
include(cmake/set_version_numbers.cmake)

add_dependency(ChimeraTK-ControlSystemAdapter REQUIRED)

# configure files required to build the ControlSystemAdapter-EPICS
list(GET ChimeraTK-ControlSystemAdapter_INCLUDE_DIRS 0 ChimeraTK-ControlSystemAdapter_INCLUDE_DIR)
list(GET ChimeraTK-ControlSystemAdapter_LIBRARY_DIRS 0 ChimeraTK-ControlSystemAdapter_LIBRARY_DIR)
configure_file(adapter/CONFIG_SITE.local.in ${PROJECT_BINARY_DIR}/adapterCONFIG_SITE.local)
configure_file(adapter/RELEASE.local.in ${PROJECT_BINARY_DIR}/adapterRELEASE.local)

# configure files required to build the IOC with the  ControlSystemAdapter-EPICS as device support
configure_file(ioc/RELEASE.in ${PROJECT_BINARY_DIR}/iocRELEASE)
configure_file(ioc/iocSrcMakefile.in ${PROJECT_BINARY_DIR}/iocSrcMakefile)

# build EPICS
add_custom_target(${PROJECT_NAME}-epics ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildEpics ${CMAKE_CURRENT_SOURCE_DIR}/epics-base
                                            WORKING_DIRECTORY ${PROJECT_BINARY_DIR})

# build the ControlSystemAdapter-EPICS
add_custom_target(${PROJECT_NAME}-adapter ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildAdapter ${CMAKE_CURRENT_SOURCE_DIR}/ChimeraTK-ControlSystemAdapter-EPICS
                                              WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                              DEPENDS ${PROJECT_NAME}-epics)

# build the IOC
set(iocSources ${PROJECT_BINARY_DIR}/src/ChimeraTKMain.cpp ${PROJECT_BINARY_DIR}/src/ChimeraTK_registerRecordDeviceDriver.cpp)
add_custom_target(${PROJECT_NAME}-ioc ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildIoc
                                          WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                          DEPENDS ${PROJECT_NAME}-adapter
                                          BYPRODUCTS ${iocSources})

# define the library
add_library(${PROJECT_NAME} SHARED ${iocSources})
add_dependencies(${PROJECT_NAME} ${PROJECT_NAME}-ioc)

include_directories(${PROJECT_BINARY_DIR}/epics-base/include)
include_directories(${PROJECT_BINARY_DIR}/epics-base/include/os/Linux)
include_directories(${PROJECT_BINARY_DIR}/epics-base/include/compiler/gcc)

file(GLOB StaticLibs "${PROJECT_BINARY_DIR}/libs/*.a")
target_link_libraries(${PROJECT_NAME} ${ChimeraTK-ControlSystemAdapter_LIBRARIES} ${StaticLibs})

set_target_properties(${PROJECT_NAME} PROPERTIES VERSION ${${PROJECT_NAME}_FULL_LIBRARY_VERSION} SOVERSION ${${PROJECT_NAME}_SOVERSION})
set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "${ChimeraTK-ControlSystemAdapter_LINKER_FLAGS} -Wl,--no-as-needed")

