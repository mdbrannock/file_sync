# File Sync
This is a fun little script to help me manage my files on my NAS. When I run it, it should read through the directories outlined in the script (specified below) and figure out which files are on my computer that aren't on the NAS, and which files are on the NAS that aren't on my computer. The computer is the source of truth, and the NAS is manipulated to match it.

# Use
There are no dependencies that aren't native to python. So while I have a `file_sync` conda environment, and specify to use it at the top of the script, it shouldn't actually matter.

Run in the terminal `~/Projects/file_sync/src/sync_files.py`. If there are any files on the NAS that aren't on the computer, you will be shown a list and a prompt for whether or not to delete them. If you don't want to delete them then enter 'n' and copy whatever files you want to keep off the NAS onto the computer. This script is just to aid in storing a backup of synced files. If you want to store something in the NAS that isn't synced, then just put it in a directory not associated with any of the ones being synced.

Currently synced directories: Documents, Projects, Videos, Music, and Pictures.

To make this useful, it's best to permanently mount the samba server. To do that, I added my login credentials to the samba server to `/home/daniel/.smbcredentials`, and added these instructions for mounting to samba server to `/etc/fstab`:

```//raspberrypi/backup /mnt/backup cifs credentials=/home/daniel/.smbcredentials,iocharset=utf8,gid=1000,uid=1000,file_mode=0777,dir_mode=0777 0 0```

For someone else to use the server, I will need to create a user for them on the samba server, instructions for which are easy to find online and I don't currently remember.


# Troubleshooting
To manually kick off a mount if the directory is not available through the samba service, use `sudo mount -a`. I added `vers=2.0` due to [this stackoverflow answer]{https://stackoverflow.com/a/73002054}. After updating PopOS we can probably get rid of it.

If the issue is that the USB drive isn't mounting to the pi, then you can try to run `sudo mount -a` on the Pi, and if it still doesn't work then investigate by running `df -h`. If the drives doesn't show up (/dev/sda1) then run `sudo blkid` to see if it's listed at all. You can look at potentially helpful error messages by running `sudo dmesg`. After that turn to the internet, because I have no clue what you're looking at.


# Improvements
* Right now metadata from directories is not kept. Cry me a river.
* Could define some functions to make this more readable with less repeated code. Could also clean up the imports, I'm just losing steam at this point.
* Could set up a cron job to run this automatically every once in a while.
* Could check to see when the last full backup was, and politely remind me to make another if it's been more than a few months.