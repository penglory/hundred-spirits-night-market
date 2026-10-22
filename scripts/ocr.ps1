param([string]$InputDirectory,[string]$OutputFile,[string]$Filter='*.png')
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null=[Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null=[Windows.Storage.FileAccessMode,Windows.Storage,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.SoftwareBitmap,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapPixelFormat,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Graphics.Imaging.BitmapAlphaMode,Windows.Graphics.Imaging,ContentType=WindowsRuntime]
$null=[Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null=[Windows.Media.Ocr.OcrResult,Windows.Foundation,ContentType=WindowsRuntime]
$null=[Windows.Storage.Streams.IRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null=[Windows.Storage.Streams.InMemoryRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]
$null=[Windows.Storage.Streams.DataWriter,Windows.Storage.Streams,ContentType=WindowsRuntime]
$generic=([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {$_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -like 'IAsyncOperation*'})[0]
function Await($operation,[Type]$resultType){
 $task=$generic.MakeGenericMethod($resultType).Invoke($null,@($operation))
 $task.Wait()
 return $task.Result
}
$engine=[Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$results=@()
foreach($file in (Get-ChildItem -LiteralPath $InputDirectory -Filter $Filter)){
 try{
  $stream=New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
  $writer=New-Object Windows.Storage.Streams.DataWriter($stream)
  $writer.WriteBytes([System.IO.File]::ReadAllBytes($file.FullName))
  $null=Await ($writer.StoreAsync()) ([uint32])
  $null=$writer.DetachStream()
  $writer.Dispose()
  $stream.Seek(0)
  $decoder=Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap=Await ($decoder.GetSoftwareBitmapAsync([Windows.Graphics.Imaging.BitmapPixelFormat]::Bgra8,[Windows.Graphics.Imaging.BitmapAlphaMode]::Ignore)) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $result=Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
  $results+=@{id=$file.BaseName;text=$result.Text;lines=@($result.Lines | ForEach-Object {$_.Text});width=$decoder.PixelWidth;height=$decoder.PixelHeight}
  $bitmap.Dispose();$stream.Dispose()
 }catch{$results+=@{id=$file.BaseName;error=$_.Exception.ToString()}}
}
[System.IO.File]::WriteAllText($OutputFile,($results | ConvertTo-Json -Depth 8),[System.Text.UTF8Encoding]::new($false))
Write-Output ("OCR completed: "+$results.Count)
