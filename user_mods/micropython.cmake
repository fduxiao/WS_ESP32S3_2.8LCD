# Library blob makes use of the heap alloc function of esp32.
add_library(blob INTERFACE)
target_sources(blob INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/blob/blob.c
)


# Add the current directory as an include directory.
target_include_directories(blob INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

# LVGL
add_library(my_lvgl INTERFACE)
include(${CMAKE_CURRENT_LIST_DIR}/lvgl/lvgl.cmake)
# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE blob my_lvgl)
