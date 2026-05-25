Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run "C:\UNREAL_ENGINE\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe ""J:\UnrealProjects\NerveSplat_v2\NerveSplat_v2.uproject"" -RenderOffScreen -PixelStreamingIP=localhost -PixelStreamingPort=8888 -game -windowed -ResX=1920 -ResY=1080", 0, False
Set shell = Nothing