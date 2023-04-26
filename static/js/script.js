const player = document.querySelector('.player')
	const playBtn = document.querySelector('.play')
	const prevBtn = document.querySelector('.prev')
	const nextBtn = document.querySelector('.next')
	const audio = document.querySelector('.audio')
	const progressContainer = document.querySelector('.progress__container')
	const progress = document.querySelector('.progress')
	const title = document.querySelector('.title')
	const imgSrc = document.querySelector('img__src')

	let songIndex = 0
	const songs = JSON.parse(document.getElementById('core').textContent)
	console.log('songs:', songs)
	console.log('song:', songs[0].song)

	const loadSong = () => {
		audio.src = `/media/${songs[songIndex].song}`
		console.log('audio:', audio)
		title.textContent = songs[songIndex].title
		console.log('title:', title)
	}

	loadSong(songs[songIndex])

	const playSong = () => {
		player.classList.add('play')
		// imgSrc.src = 'static/image/pause.svg'
		audio.play()
	}

	const pauseSong = () => {
		player.classList.remove('play')
		// imgSrc.src = 'static/image/play.svg'
		audio.pause()
	}

	playBtn.addEventListener('click', () => {
		const isPlay = player.classList.contains('play')
		if(isPlay){
			pauseSong()
		} else{
			playSong()
		}
	})

	nextBtn.addEventListener('click', e => {
		songIndex++
		if(songIndex > songs.lenght){
			songIndex = 0
		}
		loadSong(songs[songIndex])
		playSong()
	})

	prevBtn.addEventListener('click', e => {
		songIndex--
		if(songIndex < 0){
			songIndex = 0
		}
		loadSong(songs[songIndex])
		playSong()
	})

	audio.addEventListener('timeupdate', e => {
		const {duration, currentTime} = e.srcElement
		const progressPercent = (currentTime / duration) * 100
		progress.style.width = `${progressPercent}%`
		console.log('progress:', progressPercent)
		console.log('duration:', duration)
	})

	progressContainer.addEventListener('click', e => {
		const width = this.clientWidth
		const click = e.offsetX
		const duration = audio.duration
		audio.currentTime = (click / width) * duration
	})
