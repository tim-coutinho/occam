
SHELL = /bin/sh

INCLUDES = ocCore.h \
			_ocCore.h

CC = gcc
CFLAGS = -w -Wall -O2 -fPIC #-g -pg
#CFLAGS = -g 

RANLIB = ranlib
DEFS = -I.
#DEFS = -I. -DNDEBUG
#CPPFLAGS = -DTRACE_ON
LDFLAGS = -lm -lstdc++


PY_INCLUDE = /usr/include/python2.6
PY_WRAPPER = pyoccam.cpp
PY_OCCAM = occam.so

LIB = liboccam3.a
LIBOBJECTS = \
	_ocCore.o \
	ocKey.o \
	ocTable.o \
	ocVariableList.o \
	ocInput.o \
	ocRelation.o \
	ocModel.o \
	ocAttributeList.o \
	ocStateConstraint.o \
	ocManagerBase.o \
	ocRelCache.o \
	ocReport.o \
	ocModelCache.o \
	ocMath.o \
	ocOptions.o \
	ocVBMManager.o \
	ocSBMManager.o \
	ocSearchBase.o \
	ocSearch.o

EXPORTFILES = occam.so ocutils.py weboccam.py basic.py occam3 occambatch occammail.py  OpagCGI.py \
	header.html switchform.html searchform.html fitform.html logform.html base.css header.txt \
	footer.html index.html jobcontrol.py SBfitform.html weboccam.cgi

AR = ar
COMPILE = $(CC) $(DEFS) $(CFLAGS)
#CCLD = $(CC)
#LINK = $(CCLD) $(AM_CFLAGS) $(CFLAGS) $(LDFLAGS) -o $@

install: all export
all: $(LIB) $(PY_OCCAM)

export:
	cp $(EXPORTFILES) ../html
#	cp $(EXPORTFILES) install

.SUFFIXES:
.SUFFIXES: .cpp .o
clean:
	-test -z "$(LIB)" || rm -f $(LIB)
	-test -z "*.o core" || rm -f *.o core
	-test -z "*.bak" || rm -f *.bak
	-test -z "*.a" || rm -f *.a
	-test -z "*~" || rm -f *~

.cpp.o: $(INCLUDES)
	$(COMPILE) -c $<

clean-compile: clean all


$(LIB): $(LIBOBJECTS)
	-rm -f $(LIB)
	$(AR) cru $(LIB) $(LIBOBJECTS)
	$(RANLIB) $(LIB)

$(PY_OCCAM): $(LIB) $(PY_WRAPPER)
	$(COMPILE) -shared -I $(PY_INCLUDE) -o $(PY_OCCAM) $(PY_WRAPPER) $(LIB) $(LDFLAGS)

#$(PY_WRAPPER): $(PY_DEF)
#	$(SWIG) -shadow -o $(PY_WRAPPER) $(PY_DEF)

# Otherwise a system limit (for SysV at least) may be exceeded.
.NOEXPORT:
