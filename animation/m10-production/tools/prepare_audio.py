"""Immutable inputs -> measured two-pass narration; no speed/pitch/word changes."""
import argparse
import hashlib
import json
import re
import subprocess
import wave
from pathlib import Path


def run(args):
    return subprocess.run([str(x) for x in args], check=True, capture_output=True, text=True)


def measure(ffmpeg, source):
    result = run([ffmpeg, '-hide_banner', '-i', source, '-af',
                  'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'])
    return json.loads(re.findall(r'\{[^{}]+\}', result.stderr)[-1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ffmpeg', type=Path, required=True)
    parser.add_argument('--ffprobe', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    tracks, cursor, chunks = [], 0, []
    for i in range(4):
        source = args.input / f'part{i}.mp3'
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        probe = json.loads(run([args.ffprobe, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', source]).stdout)
        before = measure(args.ffmpeg, source)
        output = args.output / f'part{i}.normalized.wav'
        filt = ('loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:'
                f"measured_I={before['input_i']}:measured_TP={before['input_tp']}:"
                f"measured_LRA={before['input_lra']}:measured_thresh={before['input_thresh']}:"
                f"offset={before['target_offset']}:print_format=json")
        run([args.ffmpeg, '-y', '-hide_banner', '-i', source, '-af', filt,
             '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s24le', output])
        with wave.open(str(output), 'rb') as wav:
            frames, rate = wav.getnframes(), wav.getframerate()
            assert rate == 48000 and wav.getnchannels() == 1 and wav.getsampwidth() == 3
            chunks.append(wav.readframes(frames))
        after = measure(args.ffmpeg, output)
        assert float(after['input_tp']) <= -1.0, after
        assert abs(float(after['input_i']) + 16) < 1, after
        tracks.append({'file': source.name, 'sha256': source_hash,
                       'container_duration': float(probe['format']['duration']),
                       'decoded_samples_48k': frames, 'global_start_sample': cursor,
                       'global_end_sample': cursor + frames, 'global_start': cursor / rate,
                       'global_end': (cursor + frames) / rate,
                       'before': before, 'after': after, 'probe': probe})
        cursor += frames
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
        print(source.name, frames / rate, 's;', after['input_i'], 'LUFS;', after['input_tp'], 'dBTP', flush=True)
    master = args.output / 'HYDROOVERITY_M10_VOICE_MASTER.wav'
    with wave.open(str(master), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(3)
        wav.setframerate(48000)
        for chunk in chunks:
            wav.writeframes(chunk)
    report = {'sample_rate': 48000, 'tracks': tracks, 'total_samples': cursor,
              'duration_seconds': cursor / 48000, 'frames_at_30fps': (cursor * 30 + 47999) // 48000,
              'boundary_policy': 'Decoded PCM sample concatenation; no overlap, trimming, speed or pitch change.',
              'master_measurement': measure(args.ffmpeg, master)}
    (args.output / 'audio-measurements.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('VOICE MASTER', report['duration_seconds'], flush=True)


if __name__ == '__main__':
    main()
