PROJECT(ChimeraTK-ControlSystemAdapter-EPICS-IOC-Adapter)
cmake_minimum_required(VERSION 2.8)

include(cmake/add_dependency.cmake)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_SOURCE_DIR}/cmake ${CMAKE_CURRENT_SOURCE_DIR}/cmake/Modules)

set(${PROJECT_NAME}_MAJOR_VERSION 01)
set(${PROJECT_NAME}_MINOR_VERSION 02)
set(${PROJECT_NAME}_PATCH_VERSION 04)
include(cmake/set_version_numbers.cmake)

add_dependency(ChimeraTK-ControlSystemAdapter REQUIRED)

find_package(readline REQUIRED)


# configure files required to build the ControlSystemAdapter-EPICS
list(GET ChimeraTK-ControlSystemAdapter_INCLUDE_DIRS 0 ChimeraTK-ControlSystemAdapter_INCLUDE_DIR)
list(GET ChimeraTK-ControlSystemAdapter_LIBRARY_DIRS 0 ChimeraTK-ControlSystemAdapter_LIBRARY_DIR)
configure_file(adapter/CONFIG_SITE.local.in ${PROJECT_BINARY_DIR}/adapterCONFIG_SITE.local)
configure_file(adapter/RELEASE.local.in ${PROJECT_BINARY_DIR}/adapterRELEASE.local)

# configure files required to build the IOC with the  ControlSystemAdapter-EPICS as device support
configure_file(ioc/RELEASE.in ${PROJECT_BINARY_DIR}/iocRELEASE)
configure_file(ioc/iocSrcMakefile.in ${PROJECT_BINARY_DIR}/iocSrcMakefile)
configure_file(ioc/CONFIG_SITE.in ${PROJECT_BINARY_DIR}/iocCONFIG_SITE)

# build EPICS
add_custom_target(${PROJECT_NAME}-epics ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildEpics ${CMAKE_CURRENT_SOURCE_DIR}/epics-base
                                            WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                            BYPRODUCTS ${PROJECT_BINARY_DIR}/libs/libdbRecStd.a
                                                       ${PROJECT_BINARY_DIR}/libs/libdbCore.a 
                                                       ${PROJECT_BINARY_DIR}/libs/libca.a 
                                                       ${PROJECT_BINARY_DIR}/libs/libcas.a 
                                                       ${PROJECT_BINARY_DIR}/libs/libCom.a
                                                       ${PROJECT_BINARY_DIR}/libs/libgdd.a)

# build autosave
add_custom_target(${PROJECT_NAME}-autosave ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildAutosave ${CMAKE_CURRENT_SOURCE_DIR}/plugins/autosave
                                                WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                                DEPENDS ${PROJECT_NAME}-epics
                                                BYPRODUCTS ${PROJECT_BINARY_DIR}/libs/libautosave.a)

# build the ControlSystemAdapter-EPICS
add_custom_target(${PROJECT_NAME}-adapter ALL COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/buildAdapter ${CMAKE_CURRENT_SOURCE_DIR}/ChimeraTK-ControlSystemAdapter-EPICS ${ChimeraTK-ControlSystemAdapter_PREFIX}
                                              WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
                                              DEPENDS ${PROJECT_NAME}-autosave
                                              BYPRODUCTS ${PROJECT_BINARY_DIR}/libs/libChimeraTK-ControlSystemAdapter-EPICS.a)

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

target_link_libraries(${PROJECT_NAME} ${ChimeraTK-ControlSystemAdapter_LIBRARIES})
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libautosave.a)
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libdbRecStd.a)
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libdbCore.a)
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libca.a)
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libcas.a)
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libCom.a)
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libgdd.a)
target_link_libraries(${PROJECT_NAME} ${PROJECT_BINARY_DIR}/libs/libChimeraTK-ControlSystemAdapter-EPICS.a)
target_link_libraries(${PROJECT_NAME} ${readline_LIBRARY})

set_target_properties(${PROJECT_NAME} PROPERTIES VERSION ${${PROJECT_NAME}_FULL_LIBRARY_VERSION} SOVERSION ${${PROJECT_NAME}_SOVERSION})
set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "${ChimeraTK-ControlSystemAdapter_LINKER_FLAGS} -Wl,--no-as-needed")

# do not remove runtime path of the library when installing
set_property(TARGET ${PROJECT_NAME} PROPERTY INSTALL_RPATH_USE_LINK_PATH TRUE)

# Install the library and a template directory structure for IOCs
install(TARGETS ${PROJECT_NAME} LIBRARY DESTINATION lib)
install(FILES ${PROJECT_BINARY_DIR}/ioc/dbd/ChimeraTK.dbd DESTINATION share/${PROJECT_NAME}/iocTemplate/dbd)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/iocTemplate/iocBoot/iocChimeraTKApp/st.cmd DESTINATION share/${PROJECT_NAME}/iocTemplate/iocBoot/iocChimeraTKApp)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/iocTemplate/db/readme.txt DESTINATION share/${PROJECT_NAME}/iocTemplate/db)

set(${PROJECT_NAME}_INCLUDE_DIRS "")
set(${PROJECT_NAME}_LIBRARIES "${PROJECT_NAME} ${ChimeraTK-ControlSystemAdapter_LIBRARIES}")
set(${PROJECT_NAME}_LIBRARY_DIRS "${CMAKE_INSTALL_PREFIX}/lib")
set(${PROJECT_NAME}_CXX_FLAGS "")
set(${PROJECT_NAME}_LINK_FLAGS "${ChimeraTK-ControlSystemAdapter_LINKER_FLAGS} -Wl,--no-as-needed")
include(${CMAKE_SOURCE_DIR}/cmake/create_cmake_config_files.cmake)

