#include <Python.h>

// Función que suma dos números enteros
static PyObject* sum_func(PyObject* self, PyObject* args) {
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    return PyLong_FromLong(a + b);
}

// Métodos expuestos por la biblioteca
static PyMethodDef SumMethods[] = {
    {"add", sum_func, METH_VARARGS, "Sum two integers."},
    {NULL, NULL, 0, NULL}  // Indicador de finalización
};

// Definición del módulo
static struct PyModuleDef sum_module = {
    PyModuleDef_HEAD_INIT,
    "sum",  // Nombre del módulo
    NULL,   // Documentación
    -1,     // Estado del módulo
    SumMethods
};

// Inicialización del módulo
PyMODINIT_FUNC PyInit_sum(void) {
    return PyModule_Create(&sum_module);
}

