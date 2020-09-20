from asr_audio2text.auio_file_recognition import AudioRecognition


def main():
    result = AudioRecognition().process_from_file('./samples/sample_en.mp3')
    print(result)


if __name__ == '__main__':
    main()
