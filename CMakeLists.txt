cmake_minimum_required(VERSION 3.16)

# Change project name, based on EPICS version
if(EPICS_VERSION STREQUAL "3")
  project(ChimeraTK-ControlSystemAdapter-EPICS-IOC-Adapter)
  set(EPICS_VER "epics")
elseif(EPICS_VERSION STREQUAL "7")
  project(ChimeraTK-ControlSystemAdapter-EPICS7-IOC-Adapter)
  set(EPICS_VER "epics7")
else()
  message(FATAL_ERROR "EPICS version must be defined! Please pass to cmake command line one of the following:\n"
                      "-DEPICS_VERSION=3 to build against EPICS ver. 3.16\n"
                      "-DEPICS_VERSION=7 to build against EPICS ver. 7.02")
endif()

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake ${CMAKE_CURRENT_SOURCE_DIR}/cmake/Modules)

set(${PROJECT_NAME}_MAJOR_VERSION 02)
set(${PROJECT_NAME}_MINOR_VERSION 01)
set(${PROJECT_NAME}_PATCH_VERSION 01)
include(cmake/set_version_numbers.cmake)

find_package(ChimeraTK-ControlSystemAdapter 02.06 REQUIRED)

find_package(readline REQUIRED)
# EPICS 7 requires the Yet Another JSON Library
if(EPICS_VER STREQUAL "epics7")
  find_package(libYajl REQUIRED)
endif()

# set directory to gather all resulting libraries
set(PROJECT_LIB_DIR ${PROJECT_BINARY_DIR}/lib)

# generate a list of all epics-base libraries, depending on epics version
set(epics_BASE_LIBS ${PROJECT_LIB_DIR}/libdbRecStd.a
                    ${PROJECT_LIB_DIR}/libdbCore.a
                    ${PROJECT_LIB_DIR}/libca.a
                    ${PROJECT_LIB_DIR}/libcas.a
                    ${PROJECT_LIB_DIR}/libCom.a
                    ${PROJECT_LIB_DIR}/libgdd.a)

set(epics7_BASE_LIBS ${PROJECT_LIB_DIR}/libdbRecStd.a
                     ${PROJECT_LIB_DIR}/libdbCore.a
                     ${PROJECT_LIB_DIR}/libca.a
                     ${PROJECT_LIB_DIR}/libCom.a
                     ${PROJECT_LIB_DIR}/libnt.a
                     ${PROJECT_LIB_DIR}/libpvAccess.a
                     ${PROJECT_LIB_DIR}/libpvAccessCA.a
                     ${PROJECT_LIB_DIR}/libpvAccessIOC.a
                     ${PROJECT_LIB_DIR}/libpvaClient.a
                     ${PROJECT_LIB_DIR}/libpvData.a
                     ${PROJECT_LIB_DIR}/libpvDatabase.a
                     ${PROJECT_LIB_DIR}/libqsrv.a)

configure_file(adapter/CONFIG_SITE.local.in ${PROJECT_BINARY_DIR}/adapterCONFIG_SITE.local)
configure_file(adapter/RELEASE.local.in ${PROJECT_BINARY_DIR}/adapterRELEASE.local)

# configure files required to build the IOC with the  ControlSystemAdapter-EPICS as device support
configure_file(ioc/RELEASE.in ${PROJECT_BINARY_DIR}/iocRELEASE)
configure_file(ioc/${EPICS_VER}_iocSrcMakefile.in ${PROJECT_BINARY_DIR}/iocSrcMakefile)
configure_file(ioc/CONFIG_SITE.in ${PROJECT_BINARY_DIR}/iocCONFIG_SITE)

# build EPICS base
add_custom_target(${PROJECT_NAME}-base ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildEpics "${CMAKE_CURRENT_SOURCE_DIR}/${EPICS_VER}-base"
                                           WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                           BYPRODUCTS ${${EPICS_VER}_BASE_LIBS})

# build autosave
add_custom_target(${PROJECT_NAME}-autosave ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildAutosave ${CMAKE_CURRENT_SOURCE_DIR}/plugins/autosave
                                               WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                               DEPENDS ${PROJECT_NAME}-base
                                               BYPRODUCTS ${PROJECT_LIB_DIR}/libautosave.a)

# build calc
add_custom_target(${PROJECT_NAME}-calc ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildCalc ${CMAKE_CURRENT_SOURCE_DIR}/plugins/calc
                                           WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                           DEPENDS ${PROJECT_NAME}-base
                                           BYPRODUCTS ${PROJECT_LIB_DIR}/libcalc.a)

# build the ControlSystemAdapter-EPICS
add_custom_target(${PROJECT_NAME}-adapter ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildAdapter ${CMAKE_CURRENT_SOURCE_DIR}/ChimeraTK-ControlSystemAdapter-EPICS ${ChimeraTK-ControlSystemAdapter_PREFIX}
                                              WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                              DEPENDS ${PROJECT_NAME}-autosave
                                                      ${PROJECT_NAME}-calc
                                              BYPRODUCTS ${PROJECT_LIB_DIR}/libChimeraTK-ControlSystemAdapter-EPICS.a)

# generate the IOC sources
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

target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_LIB_DIR}/libautosave.a)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_LIB_DIR}/libcalc.a)
foreach(EPICS_BASE_LIB IN LISTS ${EPICS_VER}_BASE_LIBS)
  target_link_libraries(${PROJECT_NAME} PRIVATE ${EPICS_BASE_LIB})
endforeach()
target_link_libraries(${PROJECT_NAME} PRIVATE ChimeraTK::ChimeraTK-ControlSystemAdapter)
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_LIB_DIR}/libChimeraTK-ControlSystemAdapter-EPICS.a)
target_link_libraries(${PROJECT_NAME} PRIVATE readline)

if(EPICS_VER STREQUAL "epics7")
  # NOTICE: Due to https://github.com/lloyd/yajl/issues/209 the correct linker flag is -lyajl_s.
  # TODO: If this issue is resolved, the library might have to be changed from yail_s to yajl!
  target_link_libraries(${PROJECT_NAME} PRIVATE yajl_s)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES VERSION ${${PROJECT_NAME}_FULL_LIBRARY_VERSION} SOVERSION ${${PROJECT_NAME}_SOVERSION})

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
