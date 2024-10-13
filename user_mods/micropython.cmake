# Library blob makes use of the heap alloc function of esp32.
add_library(blob INTERFACE)
target_sources(blob INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/blob/blob.c
)


# Add the current directory as an include directory.
target_include_directories(blob INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

# Library i8080 makes use of the i80 bus of esp32.
add_library(i8080 INTERFACE)

# Add our source files to the lib
target_sources(i8080 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/i8080.c
)

# Add the current directory as an include directory.
target_include_directories(i8080 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/blob
)

# LVGL
add_library(my_lvgl INTERFACE)
include(${CMAKE_CURRENT_LIST_DIR}/lvgl/lvgl.cmake)
# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE i8080 blob my_lvgl)
