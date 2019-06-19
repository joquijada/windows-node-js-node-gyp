# Node JS on Windows+Cygwin
> This repo captures my trials and tribulations trying to success install a Node.js application that depended on a native Node.js module, [re2](http://github.com/uhop/node-re2) in this case, and that makes use of [node-gyp](https://github.com/nodejs/node-gyp) for compilation of `C++` code needed for [Node.js addons](https://nodejs.org/api/addons.html).

**Disclaimer/Caution: My approach modifying source code in the stock `node-gyp@v5.0.0` installation. Read/use this guide at your own leisure, it's not a guarantee that it will solve your issues. Ultimately you're responsible for resolving them, and making any back ups as necessary. Use this document mostly for informational purposes and I really wish it helps somebody.**

If you're like me and have already spent days trying to get Node.js applications that rely on native Node.js modules to successfully install on a Windows+Cygwin combo (perhaps even just Windows alone), then read on, as this may benefit you.

## What help is already out there?
The good news is that the Node.js community is already aware of some of the challenges faced with Node.js+Windows+native addons.
This README is based on [this guide](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules) which helps users troubleshoot Node.js issues on Windows platform.
However my situation as exacerbated by the fact that I sit inside an internal corporate network which governing team does not grant administrative rights that easily, if at all. Many solutions out there require administrative rights on your Windows machine (for example see `Option 1: Install all the required tools and configurations using Microsoft's windows-build-tools by running npm install -g windows-build-tools from an elevated PowerShell (run as Administrator).` in [this guide](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules)), of which I had none whatsoever. This meant that my options where severely abbreviated. For example I couldn't install the [windows build tools package](https://github.com/felixrieseberg/windows-build-tools) which might have alleviated my pain and suffering quicker. Instead I had to go for `Option 2: Install dependencies and configuration manually` described in [this document](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules).
I had also created [a GitHub issue](https://github.com/nodejs/node-gyp/issues/1782) seeking for some help.

## So what did I do about it?
Firs off, some hardware/software versions I work with:

* **Operating System** Microsoft Windows 10 Enterprise
* **Cygwin (exactly as spit out by `uname -a` command)** CYGWIN_NT-10.0 TNJ10038LKVTJKF 3.0.7(0.338/5/3) 2019-04-30 18:08 x86_64 Cygwin
* **Node.js** 11.9.0
* **npm** 6.9.0
* **Python (ah, the all too important python executable)**  2.7.16 (I installed this directly from Cygwin, and it **can't** be Python 3.x because it's not backwards compatible)
* **node-gyp** 5.0.0 as of the time I wrote this (I have this installed globally, `npm install -g node-gyp`)
* **Microsoft SDK Tools** Microsoft Visual Studio Professional 2017 v15.8.7/Desktop development with C++ workload

To make a long story short and after hours of painstaking debugging Python and JavaScript code and running `npm install` with `--verbose` flag, I ended up having to manually modify a handful of Python file that come with the `node-gyp` installation, plus a JavaScript Node.js file as well, and also installing missing C header `*.h` files.

All the files I modified are in a hidden .node-gyp folder of this repo which overlays over the respective path in the node-gyp folder structure. For example, `.node-gyp/lib/configure` corresponds to the `<parent path>/node-gyp/lig/configure.js` that comes with `node-gyp`. The same goes for the rest of the files I touched.

Below sections cover the issues encountered and files modified for each, in the order encountered. In the code I've added comments with the tag `CUSTOM:`, to identify code that I touched.

### ImportError: No module named gyp
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
* **Issue Description** Read the comments in the file itself. Use @edmorley observed similar, see [his comment](https://github.com/nodejs/node-gyp/issues/740#issuecomment-142467289)


### AttributeError: 'NoneType' object has no attribute 'upper'

* **File(s) Changed** None
* **Issue Description** This happened only when I ran `npm install` in a Windows CMD shell. The fix was to set locale in the environment, `set LC_ALL=en_US.UTF-8`. On a Cygwin shell I did not experience this at all

### OSError: [Errno 2] No such file or directory: ... build/binding.sln.Xyz.tmp

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

### Missing C/C++ header files
I heeded the advice given [here](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules), search for `Missing command or *.h file`

* **File(s) Changed** Nothing changed, I just added the missing `*.h` files in the place where Microsoft SDK expects them. In my case I'm using `Visual Studio 2017 Professional`, and this is the parent path where I put them: `C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Tools\MSVC\14.15.26726\include`.
You'll have to do some digging to see exactly what version you're using and the path to put them in. I just Google'ed around for that.
For your convenience I've checked the [header files I needed in this repo](.include/), find him here. They follow the same relative folder hierarchy that they should be in once installed into their final destination on the target machine.
I found many of the missing `*.h` files at [https://raw.githubusercontent.com/nodejs](https://raw.githubusercontent.com/nodejs). Others came with `node-gyp`, but you can find them only the Windows "cache" area of this package, it may be something like `C:\Users\<your user id>\AppData\Local\node-gyp\Cache\11.9.0\include` or `C:\Users\<your user id>\.node-gyp\11.9.0\include\node`

* **Issue Description** Some of the `C++` in `<your module>/node_modules/re2/lib/` will fail to compile until all missing header (`*.h`) files are found.

### LINK : fatal error LNK1181: cannot open input file

**File(s) Changed** [.node-gyp/lib/configure.js](.node-gyp/lib/configure.js)

* **Issue Description** The node lib path in the ` <AdditionalDependencies/>` node of the MS project XML file was getting messed up because the Windows style path backslashes were not escaped. For example:
`C:Usersv094303AppDataLocalnode-gypCache11.9.0x64node.lib`
There were probably other ways of dealing with this, but I went ahead and added the escaping logic in `configure.js`. Refer to [that file](.node-gyp/lib/configure.js) and search for the `CUSTOM:` tag for details on the fix.

## Other tips

### Installing `Desktop development with C++`

If you already have `Microsoft Visual Studio` installed but `npm install` warns about not being able to find the compiler, open `Microsoft Visual Studio`, enter `Desktop development with C++` in the search box, and then click to install. It was that easy for me on `Microsoft Visual Studio 2017 Professional`.

## Feedback
Questions/comments/PR's always welcomed.
