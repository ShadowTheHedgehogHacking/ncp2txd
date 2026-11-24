#v1 by Equillun, 11/22/19
#v2 by Rachus, 26/04/22

#drop a .gncp/.xncp to extract its .txd
#drop the .gncp.txd/.xncp.txd to put it back

import os, sys

OUTPUTFOLDER = "ncp2txd output"
nope = []

def endian(path):
	return 'big' if path[-4:].lower() == "gncp" else 'little'

def isNCP(path):
	return path[-4:].lower() in ("gncp", "xncp")

def extract(inDir, outDir):
	with open(inDir, "rb") as file:
		data = file.read()
	if data[:4] not in (b"FAPC", b"CPAF"):
		nope.append(inDir)
		return
	size = int.from_bytes(data[4:8], endian(inDir))
	os.makedirs(os.path.dirname(outDir) or ".", exist_ok=True)
	with open(outDir, "wb") as output:
		output.write(data[12 + size:])

def inject(txdDir):
	ncpDir = txdDir[:-4]
	with open(ncpDir, "rb") as file:
		data = file.read()
	with open(txdDir, "rb") as file:
		txd = file.read()
	e = endian(ncpDir)
	size = int.from_bytes(data[4:8], e)
	if not os.path.exists(ncpDir + ".bak"):
		with open(ncpDir + ".bak", "wb") as backup:
			backup.write(data)
	with open(ncpDir, "wb") as output:
		output.write(data[:8 + size] + len(txd).to_bytes(4, e) + txd)

try:
	K = sys.argv[1]
except IndexError:
	K = input('File or folder path: ').strip('"')

if os.path.isdir(K):
	for root, folders, files in os.walk(K):
		if OUTPUTFOLDER in root:
			continue
		for name in files:
			if isNCP(name):
				inDir = os.path.join(root, name)
				extract(inDir, os.path.join(K, OUTPUTFOLDER, os.path.relpath(inDir, K) + ".txd"))
	if len(nope) > 0:
		print('No .txd embedded in:\n' + '\n'.join(nope))
elif K[-4:].lower() == ".txd" and isNCP(K[:-4]):
	inject(K)
	print('Written to', K[:-4])
elif isNCP(K):
	extract(K, K + ".txd")
	if len(nope) > 0:
		print('This file does not have a .txd file embedded.')
		os.system("pause >nul")
else:
	print('Not a .gncp/.xncp or .gncp.txd/.xncp.txd file.')
	os.system("pause >nul")
