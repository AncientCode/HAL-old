CC=cl /nologo
CFLAGS=/EHsc /MD /GL /LD /DBUILD_PYTHON
LIBS=mpfrxx_md.lib mpfr.lib mpir.lib advapi32.lib

all: stdafx.obj HALnative.pyd ..\HALnative.pyd

clean:
	del *.lib
	del *.obj
	del *.exp

stdafx.obj: stdafx.h stdafx.cpp
	$(CC) $(CFLAGS) /c stdafx.cpp /Ycstdafx.h

.cpp.obj::
	$(CC) $(CFLAGS) /c $< /Yustdafx.h /Fpstdafx.pch

equation.obj: equation.cpp
	$(CC) $(CFLAGS) /c $**

console.cpp: console.h stdafx.h
equation.cpp: equation.h stdafx.h
HALBot.cpp: HALBot.h helper.h exception.h console.h stdafx.h

HALnative.pyd: HALBot.obj console.obj equation.obj stdafx.obj HALnative.obj
	$(CC) $(CFLAGS) /YuHALintel.pch /Fe$@ $** $(LIBS)

..\HALnative.pyd: HALnative.pyd
	copy $** $@
