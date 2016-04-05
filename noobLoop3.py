# Sean Park
# 15-112 Section P
# Term Project: NoobLoop
# Dec 10, 2015
# andrewID: spark3

from tkinter import *
from tkinter import messagebox
# to prevent aliases
import copy
# dialogboxdemo is credited to: 
# Copyright (c) 1999 by Fredrik Lundh
# This copyright applies to Dialog, askinteger, askfloat and asktring
import dialogboxdemo
# for playing multiple wav files simultaneously
import pygame
# for recording and writing new wav files
import wave, pyaudio
# for file searching, opening, copying and deleting
import os, shutil
# CMU 15-110 Sound Lab
# https://www.cs.cmu.edu/~15110/labs/lab8/index.html
# for making the metronome and countin wav files
import snd110
import tkinter as tk
# to plot waveforms and add sound effects
import numpy as np
import scipy.io.wavfile
# for math in calculating volume multipliers
import math
# for debugging to check for and fix any delays
import time

p = pyaudio.PyAudio()
width = 700
height = 500

root = Tk()
root.title("NoobLoop")
canvas = Canvas(root, width=width, height=height,background="white")
canvas.pack()

def setMenubar(menubar):
	# create a pulldown menu, and add it to the menu bar
	filemenu = Menu(menubar, tearoff=0)
	filemenu.add_command(label="New NoobLoop", command=createNewProject)
	filemenu.add_command(label="Save NoobLoop", command=saveProjButtonPressed)
	filemenu.add_command(label="Save NoobLoop as", command=saveAsButtonPressed)
	filemenu.add_command(label="Load NoobLoop", command=loadProjButtonPressed)
	filemenu.add_separator()
	filemenu.add_command(label="Exit Application", command=onWindowClose)
	menubar.add_cascade(label="File", menu=filemenu)

	metronomeMenu = Menu(menubar,tearoff=0)
	# whether the user wants the metronome while recording or not
	metronomeMenu.add_radiobutton(label="On",variable=data.metronome,
																	value=1)
	metronomeMenu.add_radiobutton(label="Off",variable=data.metronome,
																	value=0)
	menubar.add_cascade(label="Metronome",menu=metronomeMenu)

	aboutmenu = Menu(menubar, tearoff=0)
	aboutmenu.add_command(label="About NoobLoop", command=showabout)
	filemenu.add_separator()
	aboutmenu.add_command(label="Help", command=showhelp)
	menubar.add_cascade(label="About", menu=aboutmenu)

def showabout():
	messagebox.showinfo("About NoobLoop",
		"""
		NoobLoop v.1.0.0
		December 12, 2015

		Carnegie Mellon University
		15-112 Term Project
		
		Sean Park
		spark3@andrew.cmu.edu
		""")

def showhelp():
	messagebox.showinfo("Help!",
		"""
		Click the plus to add tracks!\n
		Click the star on a track to change it.

		To see an example of a project, load the 
		NoobLoop "tester"\n
		For more information, refer to text files in the 
		project's design documents and readme.txt!\n
		""")

def saveAsButtonPressed():
	print("save as button pressed.")
	projectName = dialogboxdemo.askstring("Name Your NoobLoop: ", 
											"Title:",initialvalue="example")
	# if the user exited the dialogbox, just return
	if(projectName == None):
		return
	elif(projectName.find("/") != -1 or projectName.find(",") != -1): 
		# "/" and "," cant be in the title
		messagebox.showwarning("Invalid Title.", "Please try again.")
		return
	saveFile(projectName)
	print("saved NoobLoop as %s. check trackInfo.txt for details."%projectName)
	loadFile(projectName)

def init(data):

	# VARIABLES
		data.emptyMenu = Menu(root)
		data.mode = "splashScreen"
		data.tickbox = PhotoImage(file="tickbox.gif")
		data.metronome = BooleanVar()
		data.metronome.set(0)
		data.bg1 = PhotoImage(file="splashscreen.gif")
		data.bg2 = PhotoImage(file="loopermode.gif")
		data.bg3 = PhotoImage(file="samplerbg.gif")
		data.bg4 = PhotoImage(file="changetrackmode.gif")

		data.CHUNK = 2048
		data.FORMAT = 8
		data.CHANNELS = 1
		data.RATE = 44100
		data.SAMP_WIDTH = 2

		data.mainMenuButton = Button(canvas, text="Back to Main Menu", 
			activebackground="black", command=mainMenuButtonPressed,
			overrelief=SUNKEN,bd=0,font="Architext 14 bold",bg="grey14",
			fg="white")
	
	# SPLASH SCREEN MODE
		data.newFileButton = Button(canvas, text="New NoobLoop",bd=0,
			activebackground="black",command=createNewProject,overrelief=SUNKEN,
			font="Architext 22",bg="black",fg="white",activeforeground="grey")
		data.loadProjButton = Button(canvas, text="Load NoobLoop", 
			activebackground="black",command=loadProjButtonPressed,
			activeforeground="grey",overrelief=SUNKEN,bg="black",fg="white",
			bd=0,font="Architext 20")
		data.samplerButton = Button(canvas, text="Sampler Mode",bg="black",
			activebackground="black",command=samplerButtonPressed,bd=0,
			activeforeground="grey",overrelief=SUNKEN,fg="white",
			font="Architext 20")

	# LOOPER MODE
		data.mergeButton = Button(canvas, text="Merge Selected", 
			command=mergeButtonPressed,activebackground="grey",
			bd=0,font="Architext 14",bg="grey14",fg="white",overrelief=SUNKEN)
		data.loopButton = Button(canvas, text="Loop All Tracks",bg='grey14',
			overrelief=SUNKEN,command=loopButtonPressed,activebackground="grey",
			bd=0,font="Architext 14",fg="white")
		data.newTrackButton = Button(canvas, text="+", overrelief=SUNKEN,
			command=newTrackButtonPressed,bd=0,fg="white", 
			bg="grey14",font="Architext 30")


		data.deleteTrackButton = Button(canvas, text="Delete Selected", 
			overrelief=SUNKEN,command=deleteTrackButtonPressed, fg="white",
			activebackground="grey",bd=0,font="Architext 14",bg='grey14')
		data.selectButton = Button(canvas, text="Select Tracks", 
			command=selectButtonPressed,activebackground="grey",
			bd=0,font="Architext 14",bg='grey14',fg="white",overrelief=SUNKEN)
		data.tracks =[] #list of track objects


	# CHANGETRACK MODE
		data.backToLoopsButton = Button(canvas, text="Back to Looper Mode", 
			fg="white", command=backToLoopsButtonPressed, 
			activebackground="grey", bd=0,font="Architext 14 bold",
			bg="grey14",overrelief=SUNKEN)

	# SAMPLER MODE
		data.samples = dict()

def mainMenuButtonPressed():
	print("going back to the splashScreen.")
	pygame.mixer.stop()
	data.tracks =[] #list of track objects
	data.samples = dict() # dictionary of samples in sampler mode
	data.mode = "splashScreen"

def loadProjButtonPressed():
	print("load noobloop button pressed.")
	projectName = dialogboxdemo.askstring("which one? ", "Title:",
										initialvalue="example")
	# if the user exited the dialogbox, just return
	if(projectName == None):
		return
	# if the folder doesn't exist, then just return
	if(not os.path.isdir(projectName)):
		messagebox.showwarning(
                "%s doesn't exist." % projectName,
                "Please try again.")
		return
	print("loading %s..."%projectName)
	loadFile(projectName)
	data.mode = "looper"

def samplerButtonPressed():
	print("sampler mode selected.")
	data.mode = "sampler"
	pygame.mixer.init(buffer=0)
	# generate beep noise here
	C5freq = 523.251
	noteLength = 0.4 #sec
	note = [[C5freq,noteLength]]
	write_song(note,"beep.wav")

####################################
# mode dispatcher
####################################

def mousePressed(event, data):
    if (data.mode == "splashScreen"): splashScreenMousePressed(event, data)
    if (data.mode == "looper"): looperMousePressed(event,data)
    if (data.mode == "changeTrack"): changeTrackMousePressed(event,data)
    if (data.mode == "sampler"): samplerMousePressed(event,data)

def keyPressed(event, data):
    if (data.mode == "splashScreen"): splashScreenKeyPressed(event, data)
    if (data.mode == "looper"):looperKeyPressed(event,data)
    if (data.mode == "changeTrack"):changeTrackKeyPressed(event,data)
    if (data.mode == "sampler"): samplerKeyPressed(event,data)

def timerFired(data):
    if (data.mode == "splashScreen"): splashScreenTimerFired(data)
    if (data.mode == "looper"): looperTimerFired(data)
    if (data.mode == "changeTrack"): changeTrackTimerFired(data)
    if (data.mode == "sampler"): samplerTimerFired(data)

def redrawAll(canvas, data):
    if (data.mode == "splashScreen"): splashScreenRedrawAll(canvas, data)
    if (data.mode == "looper"): looperRedrawAll(canvas,data)
    if (data.mode == "changeTrack"): changeTrackRedrawAll(canvas,data)
    if (data.mode == "sampler"): samplerRedrawAll(canvas,data)

####################################
# splashScreen mode
####################################
def splashScreenMousePressed(event, data):
	pass

def splashScreenKeyPressed(event, data):
    pass

def splashScreenTimerFired(data):
    pass

def splashScreenRedrawAll(canvas, data):
    canvas.create_image(width/2,height/2,image=data.bg1,state=NORMAL)
    root.config(menu=data.emptyMenu) # no menu on splash screen
    leftOffset = 100
    y1 = 200
    yGap = 50
    canvas.create_window(data.width - leftOffset, y1,window=data.newFileButton)
    canvas.create_window(data.width - leftOffset, y1 + yGap,
    												window=data.loadProjButton)
    canvas.create_window(data.width - leftOffset, y1 + yGap * 2,
    												window=data.samplerButton)
	

def createNewProject():
	print("New NoobLoop clicked.")
	data.projectName = dialogboxdemo.askstring("Name Your NoobLoop: ", 
												"Title:",initialvalue="example")
	# if the user exited the dialogbox, just return
	if(data.projectName == None):
		return
	elif(data.projectName.find("/") != -1 or data.projectName.find(",") != -1): 
		# "/" and "," cant be in the title
		messagebox.showwarning("Invalid Title.", "Please try again.")
		return

	data.numMeasures = dialogboxdemo.askinteger("How many measures?",
										"Number of Measures: ", initialvalue=2)
	maxMeasures = 4
	if(data.numMeasures == None): return # ditto
	elif(not 1 <= data.numMeasures <= maxMeasures):
		messagebox.showwarning("Pick a number between 1 and 4")
		return

	timeSigChoices = ['4/4','2/4','3/4','5/4']
	data.timeSig = dialogboxdemo.askstring("Pick your time signature:",
							"One of: 4/4, 3/4, 2/4 or 5/4",initialvalue="4/4")
	if(data.timeSig == None): return # ditto
	elif(data.timeSig not in timeSigChoices):
		messagebox.showwarning("Invalid time signature","Please try again.")
		return
	data.beatsPerMeasure = int(data.timeSig[0])

	data.tempo = dialogboxdemo.askinteger("Set Tempo", "Tempo:", 
															initialvalue=120)
	if(data.tempo == None): # ditto
		return
	data.secondPerBeat = 60/data.tempo # 60 secs in a min

	# set data.RECORD_SECONDS accordingly
	data.RECORD_SECONDS = (data.secondPerBeat * data.beatsPerMeasure * 
							data.numMeasures)
	# creates metronome and count-in
	createCounterWavs()
	initLooperMode()
	data.mode = "looper"

# idea inspired by CMU 15-110 Sound Lab
# https://www.cs.cmu.edu/~15110/labs/lab8/index.html
def createCounterWavs():
	# create metronome wav file
	print("creating metronome and counter files...")
	sixteenth = data.secondPerBeat / 4 # sixteenth is 1/4 of beat
	C5freq = 523.251
	G5freq = 783.991
	# 4 sixteenths in a beat. 1/16 of note, 3/16 of rest
	downbeat = [[G5freq,sixteenth],[0,sixteenth*3]]
	note = [[C5freq,sixteenth],[0,sixteenth*3]]
	measure = downbeat + note * (data.beatsPerMeasure-1)
	metronome = measure * data.numMeasures
	write_song(metronome,"%s-metronome.wav"%data.projectName)
	print("created %s-metronome.wav"%data.projectName)
	write_song(measure,"%s-countin.wav"%data.projectName)
	print("created %s-countin.wav"%data.projectName)

def write_song(song, filename):
    song_list = []
    for note in song:
        song_list = song_list + snd110.sine_tone(note[0], note[1], 1.0)
    snd110.write_wave(filename, song_list)

####################################
# looper mode
####################################

def initLooperMode():
	pygame.mixer.init(buffer=0)

	data.CHUNK = 2048
	data.FORMAT = 8
	data.CHANNELS = 1
	data.RATE = 44100
	data.SAMP_WIDTH = 2

	data.tracks =[] #list of track objects
	data.wavNum = 1

	data.looping = False
	data.selectedTracks = set()
	data.currentCommand = None

def looperMousePressed(event, data):
	if(data.currentCommand == "selecting"):
		for track in data.tracks:
			if(track.containsPoint(event)):
				print(track.trackName+" clicked.")
				if(track not in data.selectedTracks):
					data.selectedTracks.add(track)
					print(track.trackName+" selected.")
				else:
					data.selectedTracks.remove(track)
					print(track.trackName+" unselected.")
	
def looperKeyPressed(event, data):
	if(event.keysym == "m"):
		print(data.metronome.get())
	if(event.keysym == "s"):
		print("stopping all sounds.")
		pygame.mixer.stop()

def looperTimerFired(data):
	pass

def looperRedrawAll(canvas, data): 
	root.config(menu=data.menubar)
	canvas.create_image(width/2,height/2,image=data.bg2)
	topOffset = 80
	canvas.create_rectangle(0,0,width,topOffset,fill="grey14",outline=None)
	bottomOffset = 40
	canvas.create_rectangle(0,height-bottomOffset,width,height,fill="grey14",
																outline=None)
	topLeft = (90,50)
	canvas.create_text(topLeft,
		text= "NoobLoop", font = "Architext 32 bold",fill="white")
	projectNamePos = (60,100)
	canvas.create_text(projectNamePos,
		text= data.projectName, font = "Cambria 12",fill="white")
	projectInfo = "Tempo: %s\n"% str(data.tempo)
	projectInfo += "Time Signature: %s\n"% data.timeSig
	projectInfo += "%s Measures"%data.numMeasures
	projectInfoPos = (80,150)
	canvas.create_text(projectInfoPos,
		text=projectInfo, font = "Cambria 10",fill="white")
	stopLabelPos = (90, height - 100)
	canvas.create_text(stopLabelPos,
		text="Press s to stop looping", font = "Cambria 10",fill="white")
	newTrackPos = (190,40)
	delTrackPos = (270,40)
	mergePos = (400, 40)
	loopPos = (510, 40)
	selectPos = (620, 40)
	mainMenuPos = (80,480)
	canvas.create_window(newTrackPos, window=data.newTrackButton)
	canvas.create_window(delTrackPos, window=data.deleteTrackButton)
	canvas.create_window(mergePos, window=data.mergeButton)
	canvas.create_window(loopPos, window=data.loopButton)
	canvas.create_window(selectPos, window=data.selectButton)
	canvas.create_window(mainMenuPos,window=data.mainMenuButton)
	for track in data.tracks:
		track.draw(canvas)

def createWav(wavName, CHUNK,FORMAT,CHANNELS,RATE,RECORD_SECONDS,SAMP_WIDTH):

	# track name must end in .wav
	# playback is boolean
	# initialize the countin and metronome first, otherwise it lags.
	p = pyaudio.PyAudio()
	pygame.mixer.init()
	stream = p.open(format=data.FORMAT, channels=data.CHANNELS,
    			rate=data.RATE,input=True,output=False)
	metronome = None
	countin = None
	try: # if this can't be initialized, then the project must have been loaded
		metronome = pygame.mixer.Sound("%s-metronome.wav"%data.projectName)
		countin = pygame.mixer.Sound("%s-countin.wav"%data.projectName)
	except: # so find the saved metronome
		metronome = pygame.mixer.Sound("%s/%s-metronome.wav"%(data.projectName,
															  data.projectName))
		countin = pygame.mixer.Sound("%s/%s-countin.wav"%(data.projectName,
														  data.projectName))
	# PLAY COUNTIN.WAV HERE
	print("playing %s-countin.wav"%data.projectName)
	countin.play(0)
	print("played countin.")
	# multiply by 1000 to convert to ms
	oneMeasure = data.secondPerBeat * data.beatsPerMeasure * 1000
	root.after(int(oneMeasure))
	if(data.metronome.get()==1):
		print("playing metronome...")
		metronome.play(0)
		print("finished playing metronome.")
	print("creating wavFile",wavName)
	print("recording...")
	frames = []
	for i in range(math.ceil(data.RATE / data.CHUNK * data.RECORD_SECONDS)):
		sound = stream.read(CHUNK)
		frames.append(sound)
		#if(data.playback): stream.write(sound, CHUNK)
	print("done recording")
	stream.stop_stream()
	stream.close()
	p.terminate()
	#writes frames into wav file with *specifications
	wf = wave.open(wavName, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(SAMP_WIDTH)
	wf.setframerate(RATE)
	wf.writeframesraw(b''.join(frames))
	wf.close()

def merge(data):
	print("merging...")
	#if no tracks selected, caught in mergeButtonPressed
	allWavFiles = dict()
	firstTrack = None # remember what the earliest track is
	for track in data.selectedTracks:
		for wavFileName in track.sounds:
			allWavFiles[wavFileName] = track.sounds[wavFileName]
		if(firstTrack == None or 
					data.tracks.index(track) < data.tracks.index(firstTrack)):
			firstTrack = track # remember what the earliest track is
	firstTrack.sounds = allWavFiles
	print("transferred all wavFiles.", len(firstTrack.sounds))
	for track in data.selectedTracks:
		if(track != firstTrack):
			data.tracks.remove(track)
	print("removed other tracks from data.tracks.",len(data.tracks))
	for track in data.tracks:
		track.adjustPos()
		print("all track positions adjusted.")
	firstTrack.getNewCoords(firstTrack.x,firstTrack.y+firstTrack.height/2)

def playAllTracks(data):
	looping = data.looping
	for track in data.tracks:
		print("playing",track.trackName)
		numLoops = 0
		if(looping): numLoops = -1
		track.play(numLoops)
	print("played all tracks.")

def newTrackButtonPressed():
	print("new track button pressed.")
	maxMeasures = 4
	if(len(data.tracks)>=maxMeasures):
		messagebox.showwarning("Can't create any more!", 
								"Try merging some to make more.")
		return
	newTrackName = dialogboxdemo.askstring("Name Your Track: ", "Title:")
	if(newTrackName == None): return
	if(newTrackName.find("/") != -1 or newTrackName.find(",") != -1): 
		# "/" and "," cant be in the title
 		messagebox.showwarning("Invalid Track name.", "Please try again.")
 		return
	newTrack = Track(newTrackName)
	print("created new track: ",newTrack.trackName)
	data.tracks.append(newTrack)
	newTrack.adjustPos()
	print("added to data.tracks. current length:",len(data.tracks))

def mergeButtonPressed():
	print("merge button pressed.")
	if(len(data.selectedTracks) <= 1): 
		messagebox.showwarning(
                "Select two or more tracks.",
                "Please try again.")
		return
	merge(data)
	data.currentCommand = None
	data.selectedTracks = set()

def loopButtonPressed():
	print("loop button pressed.")
	data.looping = True
	playAllTracks(data)
	data.looping = False

def deleteTrackButtonPressed():
	print("delete button clicked.")
	if(len(data.selectedTracks) == 0): 
		messagebox.showwarning(
                "No tracks selected.",
                "Please try again.")
		return
	print("data.tracks",data.tracks)
	print("data.selectedTracks",data.selectedTracks)
	for track in data.selectedTracks:
		data.tracks.remove(track)
	print("selected tracks removed.")
	for track in data.tracks:
		track.adjustPos()
	print("all track positions adjusted.")
	data.currentCommand = None
	data.selectedTracks = set()

def selectButtonPressed():
	print("select button pressed.")
	if(data.currentCommand == "selecting"): 
		# if it's already selecting, get out of selecting mode
		data.currentCommand = None
		data.selectedTracks = set()
		data.selectButton.config(bg="grey14")
		print("no longer selecting.")
		return
	if(len(data.tracks) == 0):
		print("No tracks created.")
		return
	print("selecting tracks...")
	data.currentCommand = "selecting"
	data.selectButton.config(bg="grey10")

def selectTrack(event):
	print("selecting track...")
	for track in data.tracks:
		if(track.containsPoint(event)):
			print(track.trackName+" clicked.")
			data.selectedTrack = track
			print(data.selectedTrack.trackName+" selected.")
			return # return after track has been selected
	print("no track was clicked.")

def saveProjButtonPressed():
	print("save button pressed.")
	projectName = data.projectName
	print("saving file to %s..."%projectName)
	saveFile(projectName)
	print("saved. open trackInfo.txt in %s folder to check."%projectName)

def saveFile(projectName,newName=None):
	if(newName == None): newName = projectName
	try: os.mkdir(projectName)
	except: 
		messagebox.showwarning("Project has already been saved.", 
								"It has been overwritten.")
		pass
	# move the metronome and countin wavs
	metronomeName = data.projectName + "-metronome.wav"
	newmPath = newName + "/" + newName + "-metronome.wav"
	counterName = data.projectName + "-countin.wav"
	newmPath = newName + "/" + newName + "-countin.wav"
	try:
		shutil.copyfile(metronomeName,newmPath)
		shutil.copyfile(counterName,newcPath)
	except: # the project was loaded; no need to copy metronome
		pass
	# move the files & add track info
	for track in data.tracks:
		for wavFileName in track.sounds:
			if(wavFileName.find("/")!=-1):
				# reaches here if this wavFileName has already been saved.
				continue
			newPath = newName+"/%s"%wavFileName
			# copy the stuff into the new folder
			shutil.copyfile(wavFileName,newPath)
			# change the dict key for access
			track.sounds[newPath] = track.sounds[wavFileName]
			del track.sounds[wavFileName]
	# save project info (tempo, numMeasures, timeSig)
	firstLine = str(data.tempo)+","+str(data.numMeasures)+","+str(data.timeSig)
	firstLine += "\n"
	# write the changed stuff into a txt file
	txtPath = newName + "/trackInfo.txt"
	trackInfo = getTrackInfo()
	contents = firstLine + trackInfo
	writeFile(txtPath,contents)

def getTrackInfo():
	combinedInfo = ""
	for track in data.tracks:
		combinedInfo += (track.getInfo() + "\n")
	return combinedInfo

# readFile / writeFile taken from CMU 15-112 Course Notes
# http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

# readFile / writeFile taken from CMU 15-112 Course Notes
# http://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def loadFile(projectName):
	initLooperMode()
	data.projectName = projectName
	txtPath = projectName + "/trackInfo.txt"
	contents = readFile(txtPath)
	# load project info (tempo, numMeasures, timeSig)
	print("loading project info...")
	firstLine = contents.splitlines()[0]
	infoList = firstLine.split(",")
	data.tempo = int(infoList[0])
	data.secondPerBeat = 60/data.tempo
	data.numMeasures = int(infoList[1])
	data.timeSig = str(infoList[2])
	data.beatsPerMeasure = int(data.timeSig[0])
	# set data.RECORD_SECONDS accordingly
	data.RECORD_SECONDS = (data.secondPerBeat * data.beatsPerMeasure * 
							data.numMeasures)
	print("project info loaded.")
	# load tracks
	print("loading tracks...")
	newTrackList = []
	for trackLine in contents.splitlines()[1:]:
		firstComma = trackLine.index(",")
		# first 5 chars is "NAME:"
		trackName = trackLine[5:firstComma]
		print("loading %s"%trackName)
		newTrack = Track(trackName)
		newTrackList.append(newTrack)
		# load the comment
		# first 8 chars is "COMMENT:"
		commentStart = trackLine.index("COMMENT:") + 8
		nextComma = trackLine[commentStart:].index(",") + commentStart
		newTrack.comments = trackLine[commentStart:nextComma]
		# first 11 chars is "WAVE FILES:"
		wavFileStart = trackLine.index("WAVE FILES:") + 11
		# now ignore name part
		trackLine = trackLine[wavFileStart:]
		newTrackSounds = dict()
		for wavFilePath in trackLine.split(","):
			if(wavFilePath==""): continue
			newTrackSounds[wavFilePath] = pygame.mixer.Sound(wavFilePath)
		newTrack.sounds = newTrackSounds
		print("loaded %s"%trackName)
	data.tracks = newTrackList
	for track in data.tracks:
		track.adjustPos()
		track.getNewCoords(track.x,track.y+track.height/2)
	print("loaded all tracks.")

####################################
# changeTrack mode
####################################

def changeTrackRedrawAll(canvas,data):
	canvas.create_image(width/2,height/2,image=data.bg4)
	bottomRectSize = 40
	canvas.create_rectangle(0,height-bottomRectSize,width,height,fill="grey14",
																outline=None)
	logoPos = (120,50)
	canvas.create_text(logoPos,
		text= "NoobLoop", font = "Architext 32",fill="white")
	backPos = (615,480)
	canvas.create_window(backPos, window=data.backToLoopsButton)
	data.changingTrack.changeModeDraw(canvas)
	if(len(data.changingTrack.sounds) > 0):
		data.changingTrack.changeModeDrawPlot(canvas)
	# let the user pick a sound effect
	#canvas.create_window(300,360,window=data.changingTrack.labelDir)
	#canvas.create_window(300,390,window=data.changingTrack.soundEffect)
	#canvas.create_window(300,420,window=data.changingTrack.applyEffectButton)

def changeTrackKeyPressed(event,data):
	pass

def changeTrackTimerFired(data):
	pass

def changeTrackMousePressed(event,data):
	print(event.x,event.y)
	if(commentClicked(event)):
		data.changingTrack.changeComment()
	elif(trackNameClicked(event)):
		data.changingTrack.changeTrackName()

def trackNameClicked(event): # hard coded because coords are approximate
	trackx1, trackx2 = 60, 150
	tracky1, tracky2 = 120, 140
	return (trackx1 < event.x < trackx2 and tracky1 < event.y < tracky2)

def commentClicked(event): # hard coded because coords are approximate
	commentx1, commentx2 = 90, 210
	commenty1, commenty2 = 280, 310
	return (commentx1 < event.x < commentx2 and commenty1 < event.y < commenty2)

def backToLoopsButtonPressed():
	print("backToLoops button pressed.")
	data.mode = "looper"
	data.changingTrack = None
	pygame.mixer.stop()

def changePitch(wavFilePath,steps):
	# change the wav file at the path by steps
	pass
####################################
# SAMPLER MODE
####################################

def samplerRedrawAll(canvas,data):
	canvas.create_image(width/2,height/2,image=data.bg3)
	mainMenuPos = (80,480)
	canvas.create_window(mainMenuPos,window=data.mainMenuButton)
	for key in data.samples:
		data.samples[key].draw(canvas)

def samplerKeyPressed(event,data):
    allowedKeys = "qwertyuiopasdfghjklzxcvbnm1234567890"
    maxSamples = 16
    if(event.keysym not in data.samples and event.keysym in allowedKeys):
        if(len(data.samples) >= maxSamples): 
        	messagebox.showwarning("Overloaded!","Too many samples.")
        	return
        newSample = Sample(event.keysym)
        data.samples[event.keysym] = newSample
        data.samples[event.keysym].record()
        print("new sample created",event.keysym)
    elif(event.keysym in data.samples and data.samples[event.keysym].recording):
    	data.samples[event.keysym].recording = False
    elif(event.keysym in allowedKeys):
    	data.samples[event.keysym].play()
    else: messagebox.showwarning("Invalid Key","Pick an alphabet or number")

def samplerTimerFired(data):
    pass

def samplerMousePressed(event,data):
	pass
####################################
# object classes
####################################

class Track(object):
	def __init__(self, trackName):
		self.trackName = trackName
		self.sounds = dict()
		self.comments = "hihi"
		self.coords = None

		self.chunk = data.CHUNK
		self.track_format = data.FORMAT
		self.rate = data.RATE
		self.channels = data.CHANNELS
		self.track_length = data.RECORD_SECONDS
		self.sampwidth = data.SAMP_WIDTH

		self.volumes = np.array([1]*int(data.RATE*data.RECORD_SECONDS))

		self.x = 0
		self.y = 0
		self.width = 300
		self.height = 60
		#(x,y) adjusted later using self.adjustPos()

		buttonImage = PhotoImage(file="recordbutton.gif")
		self.recButton = Button(canvas, image=buttonImage,width=20,height=20,
									bg="white",command=self.recButtonPressed)
		self.recButton.image = buttonImage 

		buttonImage = PhotoImage(file="changetrackbutton.gif")
		self.changeButton = Button(canvas, image=buttonImage,width=20,height=20,
									bg="white",command=self.changeButtonPressed)
		self.changeButton.image = buttonImage 

		buttonImage = PhotoImage(file="play.gif")
		self.playButton = Button(canvas, image=buttonImage,width=20,height=20,
									bg="white",command=self.playButtonPressed)
		self.playButton.image = buttonImage

		buttonImage = PhotoImage(file="volume.gif")
		self.changeVolumeButton = Button(canvas,image=buttonImage,width=20,
				height=20,bg="white",command=self.changeVolumeButtonPressed)
		self.changeVolumeButton.image = buttonImage

		buttonImage = PhotoImage(file="mute.gif")
		self.muteButton = Button(canvas, image=buttonImage,width=20,height=20,
								bg="white",command=self.muteTrack)
		self.muteButton.image = buttonImage

	def muteTrack(self):
		for sound in self.sounds:
			# mute
			if(self.sounds[sound].get_volume() > 0):
				print("muting sound")
				self.sounds[sound].set_volume(0)
			else:
				print("unmuting sound.")
				self.sounds[sound].set_volume(1)

	def applyEffectButtonPressed(self):
		# apply the effect
		appliedEffect = self.selectedEffect.get()
		print("%s selected."%appliedEffect)
		if(appliedEffect=="None"):
			return
		elif(appliedEffect=="Reverb"):
			# apply reverb
			pass
		elif(appliedEffect=="Change Pitch"):
			# ask user how many steps they want to move up or down
			steps = dialogboxdemo.askinteger("Change Pitch",
										"Number of steps", initialvalue=0)
			# change the pitch accordingly
			for wavFileName in self.sounds:
				changePitch(wavFileName,steps)
			print("pitch changed by %s"%steps)
		elif(appliedEffect=="Boost Bass"):
			# apply reverb
			pass
		elif(appliedEffect=="Boost Treble"):
			# apply reverb
			pass

	def playButtonPressed(self):
		print("Playing %s once" % self.trackName)
		self.play(0)

	def changeTrackName(self):
		newName = dialogboxdemo.askstring("New Track Title?","",
												initialvalue=self.trackName)
		self.trackName = newName

	def changeComment(self):
		newComment = dialogboxdemo.askstring("New Comment?","",
												initialvalue=self.comments)
		if(newComment == None):
			# the user exited the dialogbox
			return
		elif(newComment.find(",") != -1):
			# display an error message
			messagebox.showwarning("Invalid Comment.", "Please try again.")
		self.comments = newComment

	def recButtonPressed(self):
		print("rec button pressed.")
		if(data.currentCommand != None):
			return
		self.record()

	def changeButtonPressed(self):
		print("change button pressed.")
		pygame.mixer.stop()
		data.mode = "changeTrack"
		data.changingTrack = self

	def record(self):
		if(len(self.sounds)!=0):
			print("there's stuff in this track's wavFiles.")
			self.sounds = dict()
			print("it's empty now.")
		global wavNum
		newWavName = self.trackName+"-"+"wav"+str(data.wavNum)+".wav"
		data.wavNum += 1
		createWav(newWavName,self.chunk,self.track_format,self.channels,
					self.rate,self.track_length,self.sampwidth)
		self.sounds[newWavName] = pygame.mixer.Sound(newWavName)
		print("added sound to %s.sounds"%self.trackName)
		print("length of self.sounds: ",len(self.sounds))
		self.getNewCoords(self.x,self.y+self.height/2)
		print("plot coords changed accordingly.")

	def play(self,numLoops):
		print("playing: ",self.trackName+"...")
		sounds = set()
		for sound in self.sounds:
			self.sounds[sound].play(numLoops)
		print("played", self.trackName)

	def draw(self,canvas):
		#draw track
		xOffset = 100
		yOffset = 10
		canvas.create_text(self.x+xOffset,self.y-yOffset,text=self.trackName,
														 fill="white")
		canvas.create_rectangle(self.x,self.y,
								self.x+self.width,self.y+self.height,
								outline="white")
		by = self.height / 3 # button y
		canvas.create_window(self.x,self.y, window=self.recButton)
		canvas.create_window(self.x,self.y + by, window=self.playButton)
		canvas.create_window(self.x,self.y + 2*by, window=self.muteButton)
		xOffset = 20
		canvas.create_window(self.x + self.width - xOffset,self.y+self.height/2, 
							 window=self.changeButton)
		if(len(self.sounds)>0): self.drawPlot(canvas,self.width,
									self.x,self.y+self.height/2,self.coords)
		if(self in data.selectedTracks):
			canvas.create_image(self.x + self.width,self.y, image=data.tickbox)

	def containsPoint(self,event):
		return ((self.x < event.x <self.x+self.width) and
				(self.y <  event.y <self.y+self.height))

	def adjustPos(self):
		print("adjusting ",self.trackName,"...")
		index = data.tracks.index(self)
		print("this is the %sth track."%index)
		self.x = 225
		yGap = 87
		firstY = 115
		self.y = index*yGap + firstY

	def getInfo(self):
		# returns all info required to re-create this track
		info = "NAME:%s" % self.trackName + ",COMMENT:"
		info += self.comments + ",WAVE FILES:"
		for wavFileName in self.sounds:
			info += wavFileName + ","
		return info

	def changeModeDraw(self,canvas):
		#draw track differently in changeTrack mode
		width = self.width * 2
		height = self.height * 2
		tlx = 50 # top left x
		tly = 150 # top left y
		canvas.create_text(tlx+30,tly-10,text=self.trackName, 
							font = "Architext 15",fill="white")
		canvas.create_rectangle(tlx,tly,tlx+width,tly+height,outline="white")
		by = height / 3
		canvas.create_window(tlx+by,tly+by/2, window=self.recButton)
		canvas.create_window(tlx+by,tly+by*3/2, window=self.playButton)
		canvas.create_window(tlx+by,tly+by*5/2, window=self.changeVolumeButton)

		# show the comments below the track
		commentPos = (150,300)
		canvas.create_text(commentPos[0],commentPos[1],text="Comments:",
								font="Arial 14 bold",fill="white")
		commentXGap = 50
		commentYGap = 30
		canvas.create_text(commentPos[0]+commentXGap,commentPos[1] +commentYGap,
						text=self.comments,font="Architext 18",fill="white")
	# function within track class
	# called on record and merge
	# replaces self.coords
	def getNewCoords(self,startX,baseY):
	  pixelsDrawn = 500
	  def getWavCoords(wavFileName):
	    data = scipy.io.wavfile.read(wavFileName)[1]
	    coords = []
	    x = startX
	    scale = 1/900
	    pixelPerSpace = 3/5
	    for i in np.linspace(0,len(data),pixelsDrawn,endpoint=False):
	      y = data[i] * scale
	      coords.append((x,y))
	      x += pixelPerSpace
	    return coords
	  def sumYVals(fileNameList):
	    # returns a list of summed YVals of the coords 
	    # of all the wavefiles in the filenamelist 
	    summedYVals = [0] * pixelsDrawn
	    for fileName in fileNameList:
	    	wavCoords = getWavCoords(fileName)
	    	wavYVals = [wavCoord[1] for wavCoord in wavCoords]
	    	summedYVals = [sum(y) for y in zip(summedYVals,wavYVals)]
	    return summedYVals
	  fileNameList = copy.deepcopy(list(self.sounds.keys()))
	  summedYVals = sumYVals(fileNameList)
	  newCoords = []
	  for i in range(len(summedYVals)):
	  	newCoords.append((i/2,summedYVals[i]))
	  self.coords = newCoords

	def changeModeDrawPlot(self,canvas):
		tlx = 50 # top left x
		tly = 150 # top left y
		trackheight = self.height * 2
		changeModeCoords = []
		for coord in self.coords:
			changeModeCoord = (coord[0]*2,coord[1]*2)
			changeModeCoords.append(changeModeCoord)
		self.drawPlot(canvas,self.width*2,tlx,tly + trackheight/2,
															  changeModeCoords)

	def drawPlot(self,canvas,width,startX,baseY,coords):
		framesDrawn = 500
		# draw the lines
		for i in range(framesDrawn-1):
			thisCoord = (coords[i][0] + startX, coords[i][1] + baseY)
			nextCoord = (coords[i+1][0] + startX, coords[i+1][1] + baseY)
			canvas.create_line(thisCoord,nextCoord,fill="white")
	  		#draw base line
		drawingWidth = width
		canvas.create_line((startX,baseY),(startX+drawingWidth,baseY),
							fill="white")

	def changeVolumeButtonPressed(self):
		print("change volume button pressed.")
		vc = Toplevel()
		vc.title("Volume Changer")
		this_vc = VolumeChanger(vc,self.volumes)

class VolumeChanger(object):

    width = 600
    height = 100

    def __init__(self,toplevel,volumeMultipliers):
        print("init called")
        self.root2 = toplevel
        self.c = Canvas(self.root2, width=self.width, height=self.height,
        				background="white")
        self.c.pack()
        self.mouse_pressed = False
        self.c.bind("<ButtonPress-1>", self.OnMouseDown)
        self.c.bind("<ButtonRelease-1>", self.OnMouseUp)

        baseY = self.height * (3/4)
        self.nodes = [(0,baseY),(self.width,baseY)]
        self.clickTime = None # when the mouse was clicked
        self.nodeClicked = None # if a node is clicked
        self.c.create_line((0,baseY),(self.width,baseY),
        					fill="light grey") #the base line

        self.savedVolumes = [] # converted into np.array later

        self.saveVolumesButton = Button(self.root2, text="Save",
					command=self.saveVolumesButtonPressed,
					activebackground="grey",bd=0,font="Architext 14",bg="white")
        self.saveVolumesButton.pack()
        self.root2.mainloop()

    def saveVolumesButtonPressed(self):
    	print("save volumes button pressed")
    	# calculate the yCoords for each of the lines drawn
    	thisTrack = data.changingTrack
    	framesPerPixel = math.ceil(data.RATE * data.RECORD_SECONDS / self.width)
    	scale = 25
    	for i in range(len(self.nodes)-1):
    		thisNode = self.nodes[i]
    		nextNode = self.nodes[i+1]
    		# multiplied by -1 because y = 0 is at the top
    		yDiff = -1*(nextNode[1] - thisNode[1])
    		xDiff = nextNode[0] - thisNode[0]
    		connectionSlope = yDiff / xDiff
    		for pixel in range(int(xDiff)):
    			# minus because y = 0 is at the top
    			pixelValue = self.height - (thisNode[1]-connectionSlope*pixel)
    			volumeMultiplier = pixelValue / scale
    			self.savedVolumes += [volumeMultiplier] * framesPerPixel 
    	# save the yValues to data.changingTrack.volumes as np.ndarray
    	self.savedVolumes = np.array(self.savedVolumes)
    	print("self.savedVolumes is now an np.array")
    	for wavFileName in thisTrack.sounds:
    		self.writeVolumes(wavFileName,self.savedVolumes)
    	thisTrack.getNewCoords(thisTrack.x,thisTrack.y+thisTrack.height/2)
    	self.root2.destroy()

    def writeVolumes(self,filePath,newVolumeData):
    	rate,oldData = scipy.io.wavfile.read(filePath)
    	newData = []
    	for i in range(len(newVolumeData)):
       		newData.append(int(oldData[i] * newVolumeData[i]))
    	newData = np.array(newData,dtype=np.int16)
    	scipy.io.wavfile.write(filePath,rate,newData)
    	data.changingTrack.sounds[filePath] = pygame.mixer.Sound(filePath)
    	print("volume changed!")

    def do_work(self):
        x = self.root2.winfo_pointerx()
        y = self.root2.winfo_pointery()
        print ("button is being pressed... %s/%s" % (x, y))

    def OnMouseDown(self, event):
        self.clickTime = time.time()
        self.mouse_pressed = True
        self.poll()

    def OnMouseUp(self, event):
      self.mouse_pressed = False
      dragThreshold = 0.5
      if(time.time() - dragThreshold < self.clickTime):
        self.createNode(event)

    def createNode(self,event):
      print("createNode called")
      nodeSize = 10
      newNode = (event.x+nodeSize/2,event.y+nodeSize/2)
      self.c.create_oval((newNode[0]-nodeSize/2,newNode[1]-nodeSize/2),
                        (newNode[0]+nodeSize/2,newNode[1]+nodeSize/2),
                        fill="black")
      self.nodes += [newNode]
      self.nodes = sorted(self.nodes,key=lambda x:x[0])
      self.connectNodes(self.c)

    def connectNodes(self,canvas):
      self.c.delete("line")
      for i in range(len(self.nodes)-1):
        self.c.create_line(self.nodes[i],self.nodes[i+1],tag="line")

    def poll(self):
        if self.mouse_pressed:
            self.do_work()
            waitTime = 250 # ms
            self.after_id = self.root2.after(waitTime, self.poll)

class Sample(object):
	def __init__(self,key):

		#pygame.mixer.init(buffer=0)

		self.CHUNK = 1024
		self.FORMAT = 8
		self.CHANNELS = 1
		self.RATE = 44100
		self.SAMP_WIDTH = 2

		self.key = key
		self.recording = True #start recording when new sample is created
		self.beep = pygame.mixer.Sound("beep.wav")
		self.sound = None
		self.lastPlayTime = None
	    
		self.x = 0
		self.y = 0
		self.setPos()
		self.size = 30

		self.button = Button(canvas,command=self.sampleClicked)

	def sampleClicked(self):
		print("sample clicked.")
		self.record()

	def setPos(self):
		index = len(data.samples)
		firstx = 100
		xgap, ygap = 70, 60
		firsty = 300
		rowLen = 8
		self.x = firstx + xgap*(index % rowLen)
		self.y = firsty + ygap*(index//rowLen)

	def record(self):
		# record for blah, break and write recorded data if not self.recording
		p = pyaudio.PyAudio()
		stream = p.open(format=data.FORMAT, channels=data.CHANNELS, 
						rate=data.RATE,input=True)
		self.beep.play(0)
		root.after(500) #length of beep is 400 ms. wait 500ms just to be safe.
		print("recording...")
		frames = []
		for i in range(int(self.RATE / self.CHUNK)): # max length of sample is 1 second
			sound = stream.read(self.CHUNK)
			frames.append(sound)
		print("done recording")

		stream.stop_stream()
		stream.close()
		p.terminate()
		#writes frames into wav file with *specifications
		wf = wave.open("%s-sample.wav"%self.key, 'wb')
		wf.setnchannels(self.CHANNELS)
		wf.setsampwidth(self.SAMP_WIDTH)
		wf.setframerate(self.RATE)
		wf.writeframesraw(b''.join(frames))
		wf.close()
		self.sound = pygame.mixer.Sound("%s-sample.wav"%self.key)

	def play(self):
		print("playing",self.key)
		self.lastPlayTime = time.time()
		self.sound.play(0)

	def draw(self,canvas):
		# if None, it means its recording
		if(self.lastPlayTime == None): fill = None
		# fill is different if self is playing
		elif(time.time() - self.lastPlayTime < 1): fill = "green"
		else: fill = None
		canvas.create_rectangle(self.x,self.y,self.x + self.size, self.y + self.size,fill=fill,outline="white")
		canvas.create_text(self.x+self.size/2,self.y+self.size/2,text=self.key.upper(),fill="white")
		canvas.create_window(self.x,self.y,window=self.button)

def onWindowClose():
	print("window close clicked.")
	if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
		root.destroy()
		print("canvas closed.")
		# delete all the tracks from this project
		if(data.mode == "splashScreen"): return
		for track in data.tracks:
			for wavFilePath in track.sounds:
				slashIndex = wavFilePath.find("/")
				topLevelName = wavFilePath[slashIndex+1:]
				try:
					# currently only deletes files after first load of save
					os.remove(topLevelName) 
				except:
					# if it can't find the file, it has already been deleted
					pass

# run framework adapted from CMU 15-112 Course Notes
# http://www.cs.cmu.edu/~112/notes/notes-oop-part1.html
def run(width=700, height=500):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    global data #globalize data for button pressed commands
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    global p
    p = pyaudio.PyAudio()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.protocol("WM_DELETE_WINDOW",onWindowClose)

    data.menubar = Menu(root)
    setMenubar(data.menubar)
    # only shown in certain modes

    root.mainloop()  # blocks until window is closed

run(width,height)
