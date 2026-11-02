# Lista continua. Los archivos se montan desde ./music.
# Liquidsoap reintenta la conexión si Icecast aún está arrancando.
music = playlist(mode="randomize", reload_mode="watch", "/music")
radio = fallback(track_sensitive=false, [music, blank()])
output.icecast(
  %mp3(bitrate=192, samplerate=44100, stereo=true),
  host="icecast",
  port=8000,
  password=environment.get("ICECAST_SOURCE_PASSWORD", "cambia-source-password"),
  mount="/live.mp3",
  name="AI RADIO LIVE",
  description="Música original creada con inteligencia artificial",
  genre="Electronic / Eclectic",
  radio
)
