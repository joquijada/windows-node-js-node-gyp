# Node JS on Windows+Cygwin
> This repo captures my trials and tribulations trying to successfully install a Node.js application that depended on a native Node.js module, [re2](http://github.com/uhop/node-re2) in this case, which makes use of [node-gyp](https://github.com/nodejs/node-gyp) for compilation of `C++` code, needed for [Node.js addons](https://nodejs.org/api/addons.html). A GitHub issue related to this exists [here](https://github.com/nodejs/node-gyp/issues/1782)

**Disclaimer/Caution: My approach involved modifying source code in the stock `node-gyp@v5.0.0` installation. Read/use this guide at your own leisure, it's not a guarantee that it will solve your issues. Make backups as necessary, and I really wish it helps somebody.**

If you're like me and have already spent days trying to get Node.js applications that rely on native Node.js modules to successfully install on a Windows+Cygwin combo (perhaps even just Windows alone), then read on, as this may benefit you. I had created [a GitHub issue for this as well](https://github.com/nodejs/node-gyp/issues/1782).

<!-- MDTOC maxdepth:6 firsth1:1 numbering:0 flatten:0 bullets:1 updateOnSave:1 -->

- [Node JS on Windows+Cygwin](#node-js-on-windowscygwin)   
   - [1. What help is already out there?](#1-what-help-is-already-out-there)   
   - [2. So what did I do about it?](#2-so-what-did-i-do-about-it)   
      - [2.1 ImportError: No module named gyp](#21-importerror-no-module-named-gyp)   
      - [2.2 AttributeError: 'NoneType' object has no attribute 'upper'](#22-attributeerror-nonetype-object-has-no-attribute-upper)
      - [2.3 OSError: [Errno 2] No such file or directory: ... build/binding.sln.Xyz.tmp](#23-oserror-errno-2-no-such-file-or-directory-buildbindingslnxyztmp)   
      - [2.4 error MSB4184: The expression "[System.IO.Path]::GetFullPath](#24-error-msb4184-the-expression-systemiopathgetfullpath)   
      - [2.5 Missing C/C++ header files](#25-missing-cc-header-files)   
      - [2.6 LINK : fatal error LNK1181: cannot open input file](#26-link-fatal-error-lnk1181-cannot-open-input-file)   
   - [3. Other tips](#3-other-tips)   
   - [Some other tips that can help make your life easier.](#some-other-tips-that-can-help-make-your-life-easier)   
      - [3.1 Installing `Desktop development with C++`](#31-installing-desktop-development-with-c)   
   - [4. Feedback](#4-feedback)   

<!-- /MDTOC -->

## 1. What help is already out there?

The good news is that the Node.js community is already aware of some of the challenges faced with Node.js+Windows+native code addons.
This README is based on [this guide](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules) which helps users troubleshoot Node.js issues on a Windows platform.
However my situation was exacerbated by the fact that I sit inside an internal corporate network which governing team does not grant administrative rights that easily, if at all. Many solutions out there require administrative rights on your Windows machine (for example see `Option 1: Install all the required tools and configurations using Microsoft's windows-build-tools by running npm install -g windows-build-tools from an elevated PowerShell (run as Administrator)` in [this guide](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules)), of which I had none whatsoever. This meant that my options where severely abbreviated. For example I couldn't install the [windows build tools package](https://github.com/felixrieseberg/windows-build-tools) which might have alleviated my pain and suffering quicker. Instead I had to go for `Option 2: Install dependencies and configuration manually` described in [this document](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules).
I had also created [a GitHub issue](https://github.com/nodejs/node-gyp/issues/1782) seeking for some help.

## 2. So what did I do about it?
Firs off, some hardware/software versions I work with:

* **Operating System** Microsoft Windows 10 Enterprise
* **Cygwin (exactly as spit out by `uname -a` command)** CYGWIN_NT-10.0 TNJ10038LKVTJKF 3.0.7(0.338/5/3) 2019-04-30 18:08 x86_64 Cygwin
* **Node.js** 11.9.0
* **npm** 6.9.0
* **Python (ah, the all too important python executable)**  2.7.16 (I installed this directly from Cygwin, and it **can't** be Python 3.x because it's not backwards compatible)
* **node-gyp** 5.0.0 as of the time I wrote this (I have this installed globally, `npm install -g node-gyp`)
* **Microsoft SDK Tools** Microsoft Visual Studio Professional 2017 v15.8.7/Desktop development with C++ workload

To make a long story short and after hours of painstaking debugging Python and JavaScript code and running `npm install` with `--verbose` flag, I ended up having to manually modify a handful of Python files that come with the `node-gyp` installation, plus a JavaScript Node.js file as well, and also installing missing C header `*.h` files. All the code changes I made I surrounded with a global boolean flag that can be set/unset in the environment (I.e. `npm config set custom_fix true` or `npm config set custom_fix false`), this way it's quick and easy to toggle on/off my patch.

All the files I modified are in hidden [.node-gyp](./.node-gyp) folder of this repo. It overlays over the respective path in the `node-gyp` installation folder structure. For example, [.node-gyp/lib/configure.js](./.node-gyp/lib/configure.js) corresponds to the `<parent path>/node-gyp/lig/configure.js` that comes with the `node-gyp` installation. The same goes for the rest of the files I touched.

Below sections cover the issues encountered and files modified for each, in the order encountered. In the code I've added comments with the tag `CUSTOM:`, to identify code that I touched.

**For your convenience, if you do decide to install the files, I have made things flag driven, so that you can easily/auto-magically toggle on/off the fixes made. To toggle on, set following `npm` environment flag via command below:**

`npm config set custom_logic true`

---

### 2.1 ImportError: No module named gyp

```
ImportError: No module named gyp
gyp ERR! configure error
gyp ERR! stack Error: `gyp` failed with exit code: 1
gyp ERR! stack     at ChildProcess.onCpExit (C:\Program Files\nodejs\node_modules\npm\node_modules\node-gyp\lib\configure.js:345:16)
gyp ERR! stack     at ChildProcess.emit (events.js:197:13)
gyp ERR! stack     at Process.ChildProcess._handle.onexit (internal/child_process.js:254:12)
gyp ERR! System Windows_NT 10.0.16299
gyp ERR! command "C:\\Program Files\\nodejs\\node.exe" "C:\\Program Files\\nodejs\\node_modules\\npm\\node_modules\\node-gyp\\bin\\node-gyp.js" "rebuild"
gyp ERR! cwd C:\...\<package name>\node_modules\re2
gyp ERR! node -v v11.9.0
gyp ERR! node-gyp -v v3.8.0
gyp ERR! not ok
npm verb lifecycle re2@1.8.4~install: unsafe-perm in lifecycle true
```

* **File(s) Changed** [.node-gyp/gyp/gyp_main.py](.node-gyp/gyp/gyp_main.py)
* **Issue Description** Read the comments in the file itself. User [@edmorley](https://github.com/nodejs/node-gyp/issues/740#issuecomment-142467289) observed similar, see [his comment](https://github.com/nodejs/node-gyp/issues/740#issuecomment-142467289)
---

### 2.2 AttributeError: 'NoneType' object has no attribute 'upper'

* **File(s) Changed** None
* **Issue Description** This happened only when I ran `npm install` in a Windows CMD shell. The fix was to set locale in the environment, `set LC_ALL=en_US.UTF-8`. On a Cygwin shell I did not experience this at all

> Note: On `PowerShell` the syntax for setting environment variables is `$Env:<var name>=<var val>`.
---

### 2.3 OSError: [Errno 2] No such file or directory: ... build/binding.sln.Xyz.tmp
```
File "/cygdrive/c/Users/<my id>/AppData/Roaming/npm/node_modules/node-gyp/gyp/pylib/gyp/MSVSNew.py", line 213, in __init__
   self.Write()
 File "/cygdrive/c/Users/<my id>/AppData/Roaming/npm/node_modules/node-gyp/gyp/pylib/gyp/MSVSNew.py", line 340, in Write
   f.close()
 File "/cygdrive/c/Users/<my id>/AppData/Roaming/npm/node_modules/node-gyp/gyp/pylib/gyp/common.py", line 396, in close
   os.unlink(self.tmp_path)
OSError: [Errno 2] No such file or directory: '/cygdrive/c/.../<pkg name>/node_modules/re2/c:\\...\\<pkg name>\\node_modules\\re2\\build/binding.sln.gyp.Qy2Qg_.tmp'
```

* **File(s) Changed** [.node-gyp/gyp/pylib/gyp/common.py](.node-gyp/gyp/pylib/gyp/common.py)
* **Issue Description** Read the comments in [this file](.node-gyp/gyp/pylib/gyp/common.py), search for `CUSTOM: Removed the "dir" argument because`
---

### 2.4 error MSB4184: The expression "[System.IO.Path]::GetFullPath
>Bellow is fuller error message, where you see `...\<my module name>` it's redactions I made to hide company secrets

```
Build started 6/20/2019 8:32:59 AM.^M
Project "C:\...\<my module name>\node_modules\re2\build\binding.sln" on node 1 (default targets).^M
ValidateSolutionConfiguration:^M
  Building solution configuration "Release|x64".^M
Project "C:\...\<my module name>\node_modules\re2\build\binding.sln" (1) is building "C:\...\<my module name>\node_modules\re2\build\re2.vcxproj" (2) on node 1 (default targets).^M
C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\MSBuild\15.0\Bin\Microsoft.Common.CurrentVersion.targets(283,5): error MSB4184: The expression "[System.IO.Path]::GetFullPath(C:\...\<my module name>\node_modules\re2\build\..\C:\...\<my module name>\node_modules\re2\build\Release\)" cannot be evaluated. The given path's format is not supported. [C:\...\<my module name>\node_modules\re2\build\re2.vcxproj]^M
Done Building Project "C:\...\<my module name>\node_modules\re2\build\re2.vcxproj" (default targets) -- FAILED.^M
Done Building Project "C:\...\<my module name>\node_modules\re2\build\binding.sln" (default targets) -- FAILED.^M
^M
Build FAILED.^M
^M
"C:\...\<my module name>\node_modules\re2\build\binding.sln" (default target) (1) ->^M
"C:\...\<my module name>\node_modules\re2\build\re2.vcxproj" (default target) (2) ->^M
```
* **File(s) Changed** [.node-gyp/gyp/pylib/gyp/generator/msvs.py](.node-gyp/gyp/pylib/gyp/generator/msvs.py)

* **Issue Description** The Python check for absolute path that takes place in function `_FixPath(path)`:

```
...
if fixpath_prefix and path and not os.path.isabs(path):
  path = os.path.join(fixpath_prefix, path)
...
```

is for some reason not detecting paths that begin with `C:\` as absolute. Not sure if it's a Cygwin config thing or what. Therefore it was ending up converting paths to the below, which is clearly incorrect (notice the `..\` in front):

`..\C:\Users\<my id>\AppData\Roaming\npm\node_modules\node-gyp\src\win_delay_load_hook.cc`

What I did was develop my own custom `_IsWindowsAbsPath(path)` function and modified the `if` above:

```
...
if (fixpath_prefix and path and not os.path.isabs(path)
      and (not gyp.common.IsCustomFixOn() or (not _IsWindowsAbsPath(path) and not path[0] == '$'))):
  path = os.path.join(fixpath_prefix, path)
...
```
---

### 2.5 Missing C/C++ header files
I heeded the advice given [here](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules), search for `Missing command or *.h file`

* **File(s) Changed** Nothing changed, I just added the missing `*.h` files in the place where Microsoft SDK expects them. In my case I'm using `Visual Studio 2017 Professional`, and this is the parent path where I put them: `C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Tools\MSVC\14.15.26726\include`.
You'll have to do some digging to see exactly what version you're using and the path to put them in. I just Google'ed around for that.
For your convenience I've checked the [header files I needed in this repo](.include/), find them [here](.include/). They follow the same relative folder hierarchy that they should be in once installed into their final destination on the target machine.
I found many of the missing `*.h` files at [https://raw.githubusercontent.com/nodejs](https://raw.githubusercontent.com/nodejs). Others came with `node-gyp`, but I was able to find them only in a special area of the Windows "cache" that may be something like `C:\Users\<your user id>\AppData\Local\node-gyp\Cache\11.9.0\include` or `C:\Users\<your user id>\.node-gyp\11.9.0\include\node`

* **Issue Description** Some of the `C++` in `<your module>/node_modules/re2/lib/` will fail to compile until all missing header (`*.h`) files are found, simple as that and no way around it. I guess it's a fact of life for those of us having to develop Node.js on Windows machines. Perhaps soon the Node.js team will address this in a more automated manner.
---

### 2.6 LINK : fatal error LNK1181: cannot open input file
* **File(s) Changed** [.node-gyp/lib/configure.js](.node-gyp/lib/configure.js)

* **Issue Description** The node lib path in the ` <AdditionalDependencies/>` node of the MS project XML file was getting messed up because the Windows style path backslashes were not escaped. For example, `C:Usersv094303AppDataLocalnode-gypCache11.9.0x64node.lib` in XML snippet below from the `<your package>/node_modules/re2/build/re2.vcxproj`, `before` and `after` snippets provided for comparison:

- Before fix
```xml
<AdditionalDependencies>kernel32.lib;user32.lib;gdi32.lib;winspool.lib;comdlg32.lib;advapi32.lib;shell32.lib;ole32.lib;oleaut32.lib;uuid.lib;odbc32.lib;DelayImp.lib;&quot;C:Usersv094303AppDataLocalnode-gypCache11.9.0x64node.lib&quot;</AdditionalDependencies>
```

- After fix
```xml
<AdditionalDependencies>kernel32.lib;user32.lib;gdi32.lib;winspool.lib;comdlg32.lib;advapi32.lib;shell32.lib;ole32.lib;oleaut32.lib;uuid.lib;odbc32.lib;DelayImp.lib;&quot;C:\Users\v094303\AppData\Local\node-gyp\Cache\11.9.0\x64\node.lib&quot;</AdditionalDependencies>
```

There were probably other ways of dealing with this, but I went ahead and added the escaping logic in `configure.js`. Refer to [that file](.node-gyp/lib/configure.js) and search for the `CUSTOM:` tag for details on the fix.

## 3. Other tips

Some other tips that can help make your life easier.

### 3.1 Installing `Desktop development with C++`
If you already have `Microsoft Visual Studio` installed but `npm install` warns about not being able to find the compiler, open `Microsoft Visual Studio`, enter `Desktop development with C++` in the search box, and then click to install. It was that easy for me on `Microsoft Visual Studio 2017 Professional`.

## 4. Feedback
Questions/comments/PR's always welcomed.
