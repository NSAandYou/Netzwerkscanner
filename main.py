import sys
import setup

if __name__ == '__main__':
    worker = setup.run(sys.argv)
    if worker is not None:
        worker.start()
