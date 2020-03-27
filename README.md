# preshus
PREServation Hash UtilitieS

or: tools for using checksums in preservation workflows

Here's a list of tools available in this repo

* hashcopy
* hashchecker

## hashcopy

**What Is It?**

hashcopy is a tool that moves files from one directory or volume to another with logged checksum verification. The verification performed by hashcopy is done using checksums held in sidecar files. Here is the workflows

* check to see if sidecar files exist for source file(s)
* if sidecar files don't exist, make them
* if sidecar files are out of date (modified date is earlier than modified date of parent file), remake them
* move all files and sidecar files
* validate any non-sidecar file once it is moved

**What Is A Sidecar File?**

A sidecar file is a plaintext file that contains the checksum of it's parent file, as well as the relative path to the parent file. Here's is the sample nesting of a sidecar file1

```
Directory
│
├── sample_file.mov
│
└── sample_file.mov.md5
```

here is the sample contents of the above sidecar file

`d025ffdc24da6411ee12caf23b2f0616 *sample_file1.gif`

the * character refers the fact that the path is relative. Since the sidecar file is nested next to the file there is nothing but the filename. This is useful for validation with other preservation tools, but isn't necessary or currently used by any preshus tools

**Logging**

It's very important for us to know if something failed. However, in some cases hundreds or thousands of files are being moved. In order to make it easier to see if there are failures, a log is created in the destination folder. The user can search for the text "ERROR" or "WARNING" to see if something went wrong. Here is the meaning of these messages

* WARNING
  * A source checksum was found to be out of dated and was recreated
* ERROR
  * A checksum was invalid after moving a file. this is very bad

**General Usage**

python hashmove.py [flags] [any number of source directories or source file full paths] [destination parent directory full path]

**to copy a file (windows filepath)**

python hashmove.py C:/path/to/file.ext C:/path/to/parent/dir

**to copy a directory (unix filepath)**

python hashmove.py /home/path/to/sourceDir/ /home/path/to/destDir/

**to copy two files and a directory (unix filepath)**

python hashmove.py /home/path/to/sourceDir1/file1 /home/path/to/sourceDir2/ /home/path/to/sourceDir3/file3 /home/path/to/destDir/

### pro-tip

## hashcopy
