#pragma once

enum PajladaResult {
    PajladaResult_OK = 0,
    PajladaResult_WrongMessageType = 1,
    PajladaResult_NotInitialized = 2,
};

enum PajladaClientSlot {
    PajladaClientSlot_None = -1,
    PajladaClientSlot_Kkona = 0,
    PajladaClientSlot_Pajaw = 1,
};
