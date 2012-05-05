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

HALBot.cpp: HALBot.h stdafx.h

HALnative.pyd: HALBot.obj stdafx.obj HALnative.obj
	$(CC) $(CFLAGS) /YuHALintel.pch /Fe$@ $** $(LIBS)

..\HALnative.pyd: HALnative.pyd
	copy $** $@
