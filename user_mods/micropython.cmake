# Create an INTERFACE library for our C module.
add_library(i8080 INTERFACE)

# Add our source files to the lib
target_sources(i8080 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/i8080.c
)

# Add the current directory as an include directory.
target_include_directories(i8080 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE i8080)
