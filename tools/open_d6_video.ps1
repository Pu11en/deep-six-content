$ErrorActionPreference='Stop'
$p=__PARAMS__ | ConvertFrom-Json
$viewer=Get-Command ffplay.exe -ErrorAction SilentlyContinue
if(-not $viewer){throw 'The installed Windows ffplay viewer was not found.'}
$folder=Join-Path ([System.IO.Path]::GetTempPath()) ('D6Video-' + $p.fingerprint.Substring(0,16))
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$target=Join-Path $folder ('Deep Six - Cut paper motion ' + $p.revision + '.mp4')
if(Test-Path -LiteralPath $target){
 if((Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLower() -ne $p.fingerprint){throw 'Existing player copy changed.'}
}else{Copy-Item -LiteralPath $p.source -Destination $target}
if((Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLower() -ne $p.fingerprint){throw 'Player copy failed verification.'}

Add-Type @'
using System;
using System.Runtime.InteropServices;
public class D6NativeVideo {
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int Left,Top,Right,Bottom;}
 [StructLayout(LayoutKind.Sequential)] public struct MONITORINFO {public int Size;public RECT Monitor,Work;public uint Flags;}
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr w);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr w,int cmd);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr w,IntPtr after,int x,int y,int cx,int cy,uint flags);
 [DllImport("user32.dll")] public static extern IntPtr MonitorFromWindow(IntPtr w,uint flags);
 [DllImport("user32.dll")] public static extern bool GetMonitorInfo(IntPtr m,ref MONITORINFO info);
 [DllImport("user32.dll")] public static extern void keybd_event(byte key,byte scan,uint flags,UIntPtr info);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr w,uint msg,IntPtr key,IntPtr data);
 public static RECT WorkArea() {
  var info=new MONITORINFO();info.Size=Marshal.SizeOf(info);
  GetMonitorInfo(MonitorFromWindow(GetForegroundWindow(),2),ref info);return info.Work;
 }
 public static bool BringForward(IntPtr w,int x,int y,int width,int height) {
  ShowWindow(w,9);
  SetWindowPos(w,new IntPtr(-1),x,y,width,height,0x0040);
  if(GetForegroundWindow()!=w){keybd_event(0x12,0,0,UIntPtr.Zero);keybd_event(0x12,0,2,UIntPtr.Zero);}
  SetForegroundWindow(w);
  SetWindowPos(w,new IntPtr(-2),0,0,0,0,0x0001|0x0002|0x0010);
  return GetForegroundWindow()==w;
 }
 public static void Pause(IntPtr w) {
  PostMessage(w,0x100,new IntPtr(0x50),new IntPtr(0x00190001));
  PostMessage(w,0x101,new IntPtr(0x50),new IntPtr(unchecked((int)0xC0190001)));
 }
 public static void Rewind(IntPtr w) {
  PostMessage(w,0x100,new IntPtr(0x25),new IntPtr(0x014B0001));
  PostMessage(w,0x101,new IntPtr(0x25),new IntPtr(unchecked((int)0xC14B0001)));
 }
}
'@
$area=[D6NativeVideo]::WorkArea()
$height=[Math]::Min(820,$area.Bottom-$area.Top-100)
$width=[int](($height-40)*9/16)+20
$x=$area.Left+[int](($area.Right-$area.Left-$width)/2)
$y=$area.Top+[int](($area.Bottom-$area.Top-$height)/2)
Get-Process -Name ffplay -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -eq $p.title} | ForEach-Object { $_.CloseMainWindow() | Out-Null }
$arguments=@('-hide_banner','-loglevel','quiet','-nostats','-window_title',('"'+$p.title+'"'),'-x',($width-20),'-y',($height-40),'-loop','0','-i',('"'+$target+'"'))
$player=Start-Process -FilePath $viewer.Source -ArgumentList $arguments -WindowStyle Minimized -PassThru
$window=[IntPtr]::Zero
for($i=0;$i -lt 60;$i++) {
 Start-Sleep -Milliseconds 100
 $player.Refresh()
 if($player.HasExited){throw 'Video viewer exited before opening its window.'}
 if($player.MainWindowHandle -ne 0){$window=$player.MainWindowHandle;break}
}
if($window -eq [IntPtr]::Zero){throw 'Native video window was not found.'}
$focused=[D6NativeVideo]::BringForward($window,$x,$y,$width,$height)
if(-not $focused){throw 'Native video window could not be brought to the foreground.'}
Start-Sleep -Milliseconds 350
[D6NativeVideo]::Pause($window)
Start-Sleep -Milliseconds 200
[D6NativeVideo]::Rewind($window)
Start-Sleep -Milliseconds 250
$foreground=[D6NativeVideo]::GetForegroundWindow() -eq $window
if(-not $foreground){throw 'The viewer lost foreground focus before confirmation.'}
@{status='foreground_pause_requested';viewer='Windows ffplay';window_title=$p.title;foreground=$foreground;pause_and_rewind_sent=$true;controls='Space plays/pauses. Esc closes.';screenshot_taken=$false} | ConvertTo-Json -Compress
