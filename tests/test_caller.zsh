source "$HOME/._exports.sh"

#	read and output 'time-quality' (along with start/end times, and elapsed)
readtaskblocks --gpgin -D "$mld_tasklogs/_worklog" --postfix ".worklog.vimgpg" quality  #2> /dev/null

#	read and output all labels
readtaskblocks --gpgin -D "$mld_tasklogs/_worklog" --postfix ".worklog.vimgpg" labels #2> /dev/null

#	read and output all 'Continue' grab items
readtaskblocks --gpgin -D "$mld_tasklogs/_worklog" --postfix ".worklog.vimgpg" grabitems -L "Continue"

#	read and output all 'Today-Tasks' items
readtaskblocks --gpgin -D "$mld_tasklogs/_worklog" --postfix ".worklog.vimgpg" todaytasks

