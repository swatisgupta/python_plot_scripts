from libc.stdint cimport uintptr_t

cdef extern from "Profile/tau_types.h"
    ctypedef char x_int8
    ctypedef short x_int16
    ctypedef int x_int32
    ctypedef long long x_int64
    ctypedef unsigned char x_uint8
    ctypedef unsigned short x_uint16
    ctypedef unsigned int x_uint32
    ctypedef unsigned long long x_uint64

cdef extern from "tau_tf_writer.h":
    ctypedef void* Ttf_FileHandleT
 
cdef extern from "tau_tf.h":
    ctypedef int (*Ttf_DefClkPeriodT)( void*, double )
    ctypedef int (*Ttf_DefThreadT)( void *, unsigned int, unsigned int, const char *)
    ctypedef int (*Ttf_EndTraceT)( void *, unsigned int, unsigned int)
    ctypedef int (*Ttf_DefStateGroupT)( void *, unsigned int, const char *)
    ctypedef int (*Ttf_DefStateT)( void *, unsigned int, const char *, unsigned int )
    ctypedef int (*Ttf_EnterStateT)( void*, double, unsigned int, unsigned int, unsigned int )
    ctypedef int (*Ttf_LeaveStateT)( void*, double, unsigned int, unsigned int, unsigned int )
    ctypedef int (*Ttf_SendMessageT)( void* , double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int )
    ctypedef int (*Ttf_RecvMessageT)( void*, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int )
    ctypedef int (*Ttf_DefUserEventT)( void *, unsigned int, const char *, int )
    ctypedef int (*Ttf_EventTriggerT)( void *, double, unsigned int, unsigned int, unsigned int, long long )

    cdef struct Ttf_Callbacks:
        void*  UserData 
        Ttf_DefClkPeriodT  DefClkPeriod
        Ttf_DefThreadT     DefThread
        Ttf_DefStateGroupT DefStateGroup
        Ttf_DefStateT      DefState
        Ttf_EndTraceT      EndTrace
        Ttf_EnterStateT    EnterState
        Ttf_LeaveStateT    LeaveState
        Ttf_SendMessageT   SendMessage
        Ttf_RecvMessageT   RecvMessage
        Ttf_DefUserEventT   DefUserEvent
        Ttf_EventTriggerT   EventTrigger

    ctypedef Ttf_Callbacks Ttf_CallbacksT

    Ttf_FileHandleT Ttf_OpenFileForInput( const char *name , const char *edf)
    #void Ttf_SetSubtractFirstTimestamp( Ttf_FileHandleT handle, int value )
    #void Ttf_SetNonBlocking( Ttf_FileHandleT handle, int value )
    #int Ttf_AbsSeek( Ttf_FileHandleT handle, int eventPosition ) 
    #int Ttf_RelSeek( Ttf_FileHandleT handle, int plusMinusNumEvents ) 
    int Ttf_ReadNumEvents( Ttf_FileHandleT fileHandle, Ttf_CallbacksT callbacks, int numberOfEvents )
    Ttf_FileHandleT Ttf_CloseFile( Ttf_FileHandleT fileHandle )

def py_Ttf_OpenFileForInput(name: bytes, edf: bytes) -> :
    Ttf_OpenFileForInput(name, edf)

def py_Ttf_ReadNextEvent(fileHandle: Ttf_FileHandleT) -> int:
    cdef Ttf_CallbacksT callbacks
    Ttf_ReadNumEvents( fileHandle, callbacks, 1 )

def py_Ttf_CloseFile(name: bytes, edf: bytes) -> Ttf_FileHandleT:
    Ttf_CloseFile( fileHandle )
