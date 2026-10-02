"""Read only guest RAM from the exact isolated QA process after its fault."""
import argparse,ctypes,json,re,struct
from pathlib import Path
from ctypes import wintypes
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();folder=ROOT/'work/scratch/release064-runtime';s=json.loads((folder/'session.json').read_text('utf-8-sig'));log=(folder/'runtime.log').read_text()
 guest,host=re.findall(r'Bad memory access detected! ([0-9A-Fa-f]+) \(([0-9A-Fa-f]+)\)',log)[-1];base=int(host,16)-int(guest,16)
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE;k.CloseHandle.argtypes=[wintypes.HANDLE];k.QueryFullProcessImageNameW.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.LPWSTR,ctypes.POINTER(wintypes.DWORD)];k.ReadProcessMemory.argtypes=[wintypes.HANDLE,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
 h=k.OpenProcess(0x410,False,s['pid']);assert h,ctypes.get_last_error()
 try:
  path=ctypes.create_unicode_buffer(32768);n=wintypes.DWORD(len(path));assert k.QueryFullProcessImageNameW(h,0,path,ctypes.byref(n));assert Path(path.value).resolve()==folder/'PPSSPPWindows64.exe'
  def read(ptr,size):
   assert 0x08800000<=ptr<ptr+size<=0x0a000000;data=ctypes.create_string_buffer(size);got=ctypes.c_size_t();assert k.ReadProcessMemory(h,base+ptr,data,size,ctypes.byref(got)),ctypes.get_last_error();assert got.value==size;return data.raw
  regions={}
  for ptr,size in [(0x09fff110,1024),(0x098c82a0,192),(0x098c8300,224),(0x08da8d00,256)]:
   raw=read(ptr,size);regions[hex(ptr)]=[hex(v) for v in struct.unpack('<'+'I'*(size//4),raw)]
  owner=struct.unpack('<I',read(0x09fff140+612,4))[0]
  header=read(owner,32);regions[hex(owner)]=[hex(v) for v in struct.unpack('<8I',header)]
  for off in (4,12):
   ptr=struct.unpack_from('<I',header,off)[0];raw=read(ptr,128);regions[hex(ptr)]=[hex(v) for v in struct.unpack('<32I',raw)]
  report=dict(pid=s['pid'],guest_fault=guest,guest_regions=regions);print(json.dumps(dict(mode='write' if a.write else 'inspect',report=report),indent=2),flush=True)
  if a.write:(folder/'fault-guest-context.json').write_text(json.dumps(report,indent=2)+'\n')
 finally:k.CloseHandle(h)
if __name__=='__main__':main()
