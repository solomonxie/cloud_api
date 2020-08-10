from asr_audio2text.auio_file_recognition import recognize_audio_file


def main():
    path = './samples/sample.mp3'
    recognize_audio_file(path)


if __name__ == '__main__':
    main()
