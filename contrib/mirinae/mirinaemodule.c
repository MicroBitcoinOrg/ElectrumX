// Copyright (c) 2018 iamstenman
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <Python.h>

#include "crypto/sph/sph_groestl.h"
#include "crypto/kupyna/kupyna_tables.h"
#include "crypto/kupyna/kupyna512.h"

void MirinaeHash(const char* input, char* output, size_t length, int height)
{
    unsigned char hash[64] = { 0 };
    unsigned char offset[64] = { 0 };
    unsigned char seed[32] = { 0 };
    const int window = 256;
    const int aperture = 32;
    int64_t n = 0;

    sph_groestl512_context ctx_groestl;
    struct kupyna512_ctx_t ctx_kupyna;
    memcpy(seed, input + 4, (36 - 4) * sizeof(*input));

    kupyna512_init(&ctx_kupyna);
    kupyna512_update(&ctx_kupyna, seed, 32);
    kupyna512_final(&ctx_kupyna, offset);
    memcpy(&n, offset, 8);

    sph_groestl512_init(&ctx_groestl);
    sph_groestl512(&ctx_groestl, input, length);
    sph_groestl512_close(&ctx_groestl, hash);

    unsigned int light = (hash[0] > 0) ? hash[0] : 1;
    for (unsigned int i = 0; i < (((n % height) + (height + 1)) % window); i++) {
        unsigned int inner_loop = (light % aperture);
        for (unsigned int j = 0; j < inner_loop; j++) {
            kupyna512_init(&ctx_kupyna);
            kupyna512_update(&ctx_kupyna, hash, 64);
            kupyna512_final(&ctx_kupyna, hash);
        }

        light = (hash[inner_loop] > 0) ? hash[inner_loop] : 1;
    }

    sph_groestl512_init(&ctx_groestl);
    sph_groestl512(&ctx_groestl, hash, 64);
    sph_groestl512_close(&ctx_groestl, hash);

    memcpy(output, hash, 32);
}

static PyObject *mirinae_gethash(PyObject *self, PyObject *args)
{
    char *output;
    PyObject *value;
#if PY_MAJOR_VERSION >= 3
    PyBytesObject *input;
#else
    PyStringObject *input;
#endif
    int length;
    int height;
    if (!PyArg_ParseTuple(args, "Sii", &input, &length, &height))
        return NULL;
    Py_INCREF(input);
    output = PyMem_Malloc(32);

#if PY_MAJOR_VERSION >= 3
    MirinaeHash((char *)PyBytes_AsString((PyObject*) input), output, length, height);
#else
    MirinaeHash((char *)PyString_AsString((PyObject*) input), output, length, height);
#endif
    Py_DECREF(input);
#if PY_MAJOR_VERSION >= 3
    value = Py_BuildValue("y#", output, 32);
#else
    value = Py_BuildValue("s#", output, 32);
#endif
    PyMem_Free(output);
    return value;
}

static PyMethodDef MirinaeHashMethods[] = {
    { "get_hash", mirinae_gethash, METH_VARARGS, "Returns result of Mirinae hash" },
    { NULL, NULL, 0, NULL }
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef MirinaeHashModule = {
    PyModuleDef_HEAD_INIT,
    "mirinae",
    "...",
    -1,
    MirinaeHashMethods
};

PyMODINIT_FUNC PyInit_mirinae(void) {
    return PyModule_Create(&MirinaeHashModule);
}

#else

PyMODINIT_FUNC initmirinae(void) {
    (void) Py_InitModule("mirinae", MirinaeHashMethods);
}
#endif
