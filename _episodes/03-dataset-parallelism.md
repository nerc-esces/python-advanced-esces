---
title: "Dataset Parallelism"
teaching: 15
exercises: 10
questions:
- "How do we apply the same command to every file or parameter in a dataset?"
objectives:
- "Use GNU Parallel to apply the same command to every file or parameter in a dataset"
keypoints:
- "GNU Parallel can apply the same command to every file in a dataset"
- "GNU Parallel works on the command line and doesn't require Python, but it can run multiple copies of a Python script"
- "It is often the simplest way to apply parallelism"
- "It requires a problem that works independently across a set of files or a range of parameters"
- "Without invoking a more complex job scheduler, GNU Parallel only works on a single computer"
- "By default GNU Parallel will use every CPU core available to it"
---

# Dataset Parallelism with GNU Parallel

GNU Parallel is a very powerful command that lets us execute any command in parallel. To do this effectively we need what is often called an "embarrasingly parallel" problem.
These are problems where a dataset can be split into several parts and each can be processed independently and simultaneously. Such problems often occur when a dataset is
split across multiple files or there are multiple parameters to process.

## Basic use of GNU Parallel

First we will use an example dataset of five NetCDF files.

```
mkdir parallel-data
cd parallel-data
curl {{ site.url }}{{ site.baseurl }}/data/parallel-data.tar.gz > parallel-data.tar.gz
tar xvfz parallel-data.tar.gz
cd ..
```
{: .language-bash}


In the Unix shell we could loop over a dataset one item at a time by using a for loop and the ls command together.

```
for file in $(ls) ; do
    echo $file
done
```
{: .language-bash}

We can ask GNU parallel to perform the same task and at least several of the echo commands will run simultaneously.
The `{1}` after the echo will be substituted by what ever comes after `:::`, in this case the output of the ls command.

```
parallel echo {1} ::: $(ls)
```
{: .language-bash}

We could also use a set of values instead of ls:

```
parallel echo {1} ::: 1 2 3 4 5 6 7 8
```
{: .language-bash}

Just running echo commands isn't very useful, but we could use parallel to invoke a Python script too.
The serial example to process a series of NetCDF files would be:

```
for file in $(ls parallel-data/*.nc) ; do
    python summary.py $file
done
```
{: .language-bash}

And with parllel it would be:

```
parallel python myscript.py {1} ::: $(ls parallel-data/*.nc)
```
{: .language-bash}

## Citing Software

It is good practice to cite the software we use in research. GNU Parallel is particularly vocal about this and it will remind you to cite it.
Running `parallel --citation` will show us all of the information we'll need if we are going to cite it in a publication, it will also prevent further reminders about it.

## Working with multiple arguments

The `{1}` can be used multiple times if we want the same argument to be repeated.
If for example the script required an input and output file name and the output was the input file with .out on the end, then we could do the following:

```
parallel python myscript-2.py {1} {1}.out ::: $(ls parallel-data/*.nc)
```
{: .language-bash}

## Using a list of files stored in a file

Using commands or lists of arguments is fine for many use cases, but sometimes there are cases where we might want to use a list of files in a text file.
For this we use the `::::` (note four, not three :s) separator and specify the file name after that, each line in file will be used as a line of input.

~~~
ls *.nc | grep "^ABC" > files.txt
parallel python myscript-2.py {1} {1}.out :::: files.txt
~~~
{: .language-bash}

## More complex arguments

Parallel can also run two (or more) sets of arguments, the first argument will become `{1}`, the second `{2}` and so on. Each argument's input list must be separated by a `:::`.

```
parallel echo "hello {1} {2}" ::: 1 2 3 ::: a b c
```
{: .language-bash}

We can also mix the `:::` and `::::` notations to have some arguments come from files and others from lists.
For example, if we had a list of netcdf files in files.txt, and you wanted to perform an analysis of two of the varibles, we could use:

```
parallel process.py --variable={1} {2} ::: temp sal :::: files.txt
```
{: .language-bash}

`{1}` will be substituted for temp or sal, while `{2}` will be given the filenames. Parallel will run process.py for both variables on every file.

### Pairing arguments

Sometimes we don't want to run every variable with every other variable, but will want to run them in pairs, for example:

```
parallel echo "hello {1} {2}" ::: 1 2 3 :::+ a b c
```
{: .language-bash}

which produces:

```
hello world 1 a
hello world 2 b
hello world 3 c
```
{: .output}

## Job Control

By default Parallel will use every processing core on the system. Sometimes, especially on shared systems this isn't what we want to do.
On some HPC systems we might only be allocated a few cores, but the system will have many more and Parallel will try to use them all.
Depending on how the system is configured that will either cause us to run several processes on each core we're allocated or to exceed our allocation.
We can tell Parallel to limit how many cores it is running on with the `--max-procs` argument.

## Logging

In more complex jobs it can be useful to have a log of which jobs ran, when they started and how long they took.
This is set with the `--joblog` option to Parallel and is followed by a file name. For example:

```
parallel --joblog=jobs.log echo {1} ::: 1 2 3 4 5 6 7 8 9 10
```
{: .language-bash}

After Parallel has finished we can look at the contents of the file `jobs.log` and see the output:

~~~
Seq     Host    Starttime       JobRuntime      Send    Receive Exitval Signal  Command
1       :       1711502183.024       0.002      0       2       0       0       echo 1
2       :       1711502183.025       0.003      0       2       0       0       echo 2
3       :       1711502183.026       0.003      0       2       0       0       echo 3
4       :       1711502183.028       0.002      0       2       0       0       echo 4
5       :       1711502183.029       0.003      0       2       0       0       echo 5
6       :       1711502183.030       0.003      0       2       0       0       echo 6
7       :       1711502183.032       0.003      0       2       0       0       echo 7
8       :       1711502183.034       0.004      0       2       0       0       echo 8
9       :       1711502183.036       0.002      0       2       0       0       echo 9
10      :       1711502183.037       0.003      0       3       0       0       echo 10
~~~
{: .output}

> ## Timing the speed up with Parallel
> There is a script included with the example dataset called plot_tempanomaly.py.
> This script will plot a map of the temperature anomaly data from our GISS dataset. It takes three arguments, the name of the NetCDF file to use, a start year (specified with --start)
> and an end year (specified with --end). It will create a PNG file for each month that it processes.
>
> For example to run this for the year 2000 we would run:
>
> `python plot_tempanomaly.py gistemp1200-21c.nc --start 2000 --end 2001`
>
> We can time how long a command takes by prefixing it with the `time` command, this will return three numbers:
>
> - real: how long the whole command took to run
> - user: how much time the command used the processor for in user mode, this is typically within our code and the libraries it calls.
> - sys: how much time the command used the processor for in system mode, this typically means the time spent waiting for hardware devices to respond, for example the disk, screen or network.
> The sys and user time can exceed the real time when multiple processor cores are used.
>
> Run this for the years 2000 to 2023 as a serial job with the commands:
> ~~~
> time for year in $(seq 2000 2023) ; do python plot_tempanomaly.py gistemp1200-21c.nc --start $year --end $[$year+1] ; done
> ~~~
> {: .language-bash}
>
> Now repeat the command using Parallel:
> ~~~
> time parallel python plot_tempanomaly.py gistemp1200-21c.nc --start {1} --end {2} ::: $(seq 2000 2023) :::+ $(seq 2001 2024)
> ~~~
> {: .language-bash}
>
> Note that if you are using parallel from outside of Jupyter lab then you running parallel decativates your conda/mamba environment. The easiest solution to this is to
> create a wrapper shell script that runs the python command. Type the following into your favourite text editor and save it as `plot_tempanomaly.sh`.
> ~~~
> #!/bin/bash
> python plot_tempanomaly.py $1 --start $2 --end $3
> ~~~
> {: .language-bash}
>
> ~~~
> time parallel bash plot_tempanomaly.sh gistemp1200-21c.nc {1} {2} ::: $(seq 2000 2023) :::+ $(seq 2001 2024)
> ~~~
> {: .language-bash}
>
>
> Compare the runtimes of the parallel and serial versions.
> Try adding the joblog option and examining how many jobs launched at once.
> How many jobs did Parallel launch simultaneously? How much faster was the parallel version than the serial version?
> Try adding the --max-procs option and setting this to 2,4 or 8 and compare the run time.
>
{: .challenge}

> ## Bonus Challenge: Make a Movie
>
> We now have 288 PNG images covering the time period of our dataset. A useful way to view these would be as a video.
> There are a number of programs you can use to convert these into a video file. One such program is [FFmpeg](https://ffmpeg.org).
> You might need to install FFmpeg via Conda/Mamba. Lookup in the [FFmpeg documentation](https://trac.ffmpeg.org/wiki/Slideshow) how to
> make your images into a video. Create the video, download it to your computer (you can't play it in Jupyter Lab) and play it.
>
>> ## Solution
>> FFmpeg has a choice of a few different codecs (compression algoithms), a sensible choice for a modern video player is x264.
>> You can get a list of these by running `ffmpeg -encoders`, anything starting with "V" is a video codec. Windows Media Player
>> has problems with the default output from FFmpeg using the libx264 option, but adding the argument `-pix_fmt yuv420p` seems to fix this.
>> Other media players such as [VLC](https://videolan.org) should have no problem playing video made without this.
>> ~~~
>> ffmpeg -framerate 25 -pattern_type glob -i "*.png" -vcodec libx264 -pix_fmt yuv420p output.mp4
>> ~~~
>> {: .language-bash}
> {: .solution}
{: .challenge}


{% include links.md %}
