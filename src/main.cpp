#include "types.h"

#include <cstdlib>

#if NOTWORK_BUILD
#define NOTWORK_EXPORT_API __declspec(dllexport)
#else
#define NOTWORK_EXPORT_API __attribute__((__visibility__("default")))
#endif

namespace {

// lol
int PajladaFunctionThatShouldNotBeExported() { return 0; }

}  // namespace

extern "C" {

/**
 * lol to free a string just put the char pointer here xd
 **/
PajladaResult NOTWORK_EXPORT_API PajladaFreeString(char *c) {
    free(c);

    return PajladaResult_OK;
}

// Initialize pajlada
PajladaResult NOTWORK_EXPORT_API PajladaInit(PajladaClientSlot slot,
                                             const char *name) {
    return PajladaResult_OK;
}

/**
 * Release pajlada
 **/
PajladaResult NOTWORK_EXPORT_API PajladaRelease() { return PajladaResult_OK; }

/**
 * Close pajlada. PajladaRelease must have been called before this function
 **/
PajladaResult NOTWORK_EXPORT_API PajladaClose() { return PajladaResult_OK; }

}  // extern "C"
