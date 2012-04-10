/*
live_segmenter.c
Copyright (c) 2012 Thorsten Philipp <kyrios@kyri0s.de>
* Originaly modified by and Copyright (c) 2009 Carson McDonald
* Originaly created by and Copyright (c) 2009 Chase Douglas

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in the 
Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the
following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/


#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "libavformat/avformat.h"



struct config_info
{
  const char *input_filename;
  int segment_length;
  const char *temp_directory;
  const char *filename_prefix;
  const char *encoding_profile;
};

static AVStream *add_output_stream(AVFormatContext *output_format_context, AVStream *input_stream) 
{
  AVCodecContext *input_codec_context;
  AVCodecContext *output_codec_context;
  AVStream *output_stream;

  output_stream = av_new_stream(output_format_context, 0);
  if (!output_stream) 
  {
    fprintf(stderr, "Segmenter error: Could not allocate stream\n");
    exit(1);
  }

  input_codec_context = input_stream->codec;
  output_codec_context = output_stream->codec;

  output_codec_context->codec_id = input_codec_context->codec_id;
  output_codec_context->codec_type = input_codec_context->codec_type;
  output_codec_context->codec_tag = input_codec_context->codec_tag;
  output_codec_context->bit_rate = input_codec_context->bit_rate;
  output_codec_context->extradata = input_codec_context->extradata;
  output_codec_context->extradata_size = input_codec_context->extradata_size;

  if(av_q2d(input_codec_context->time_base) * input_codec_context->ticks_per_frame > av_q2d(input_stream->time_base) && av_q2d(input_stream->time_base) < 1.0/1000) 
  {
    output_codec_context->time_base = input_codec_context->time_base;
    output_codec_context->time_base.num *= input_codec_context->ticks_per_frame;
  }
  else 
  {
    output_codec_context->time_base = input_stream->time_base;
  }

  switch (input_codec_context->codec_type) 
  {
    case CODEC_TYPE_AUDIO:
      output_codec_context->channel_layout = input_codec_context->channel_layout;
      output_codec_context->sample_rate = input_codec_context->sample_rate;
      output_codec_context->channels = input_codec_context->channels;
      output_codec_context->frame_size = input_codec_context->frame_size;
      if ((input_codec_context->block_align == 1 && input_codec_context->codec_id == CODEC_ID_MP3) || input_codec_context->codec_id == CODEC_ID_AC3) 
      {
        output_codec_context->block_align = 0;
      }
      else 
      {
        output_codec_context->block_align = input_codec_context->block_align;
      }
      break;
    case CODEC_TYPE_VIDEO:
      output_codec_context->pix_fmt = input_codec_context->pix_fmt;
      output_codec_context->width = input_codec_context->width;
      output_codec_context->height = input_codec_context->height;
      output_codec_context->has_b_frames = input_codec_context->has_b_frames;

      if (output_format_context->oformat->flags & AVFMT_GLOBALHEADER) 
      {
          output_codec_context->flags |= CODEC_FLAG_GLOBAL_HEADER;
      }
      break;
    default:
      break;
  }

  return output_stream;
}

void output_transfer_command(const unsigned int first_segment, const unsigned int last_segment, const int end, const char *encoding_profile, const double duration)
{
  char buffer[1024 * 10];
  memset(buffer, 0, sizeof(char) * 1024 * 10);

  sprintf(buffer, "%d, %d, %d, %s, %.2f", first_segment, last_segment, end, encoding_profile,duration);

  fprintf(stderr, "segmenter: %s\n\r", buffer);
}

int main(int argc, char **argv)
{
  if(argc != 5)
  {
    fprintf(stderr, "Usage: %s <segment length> <output location> <filename prefix> <encoding profile>\n", argv[0]);
    return 1;
  }

  struct config_info config;

  memset(&config, 0, sizeof(struct config_info));

  config.segment_length = atoi(argv[1]); 
  config.temp_directory = argv[2];
  config.filename_prefix = argv[3];
  config.encoding_profile = argv[4];
  config.input_filename = "pipe://1";

  char *output_filename = malloc(sizeof(char) * (strlen(config.temp_directory) + 1 + strlen(config.filename_prefix) + 13));
  if (!output_filename) 
  {
    fprintf(stderr, "Segmenter error: Could not allocate space for output filenames\n");
    exit(1);
  }

  // ------------------ Done parsing input --------------

  av_register_all();

  AVInputFormat *input_format = av_find_input_format("mpegts");
  if (!input_format) 
  {
    fprintf(stderr, "Segmenter error: Could not find MPEG-TS demuxer\n");
    exit(1);
  }

  AVFormatContext *input_context = NULL;
  int ret = av_open_input_file(&input_context, config.input_filename, input_format, 0, NULL);
  if (ret != 0) 
  {
    fprintf(stderr, "Segmenter error: Could not open input file, make sure it is an mpegts file: %d\n", ret);
    exit(1);
  }

  if (av_find_stream_info(input_context) < 0) 
  {
    fprintf(stderr, "Segmenter error: Could not read stream information\n");
    exit(1);
  }

#if LIBAVFORMAT_VERSION_MAJOR >= 52 && LIBAVFORMAT_VERSION_MINOR >= 45
  AVOutputFormat *output_format = av_guess_format("mpegts", NULL, NULL);
#else
  AVOutputFormat *output_format = guess_format("mpegts", NULL, NULL);
#endif
  if (!output_format) 
  {
    fprintf(stderr, "Segmenter error: Could not find MPEG-TS muxer\n");
    exit(1);
  }

  AVFormatContext *output_context = avformat_alloc_context();
  if (!output_context) 
  {
    fprintf(stderr, "Segmenter error: Could not allocated output context");
    exit(1);
  }
  output_context->oformat = output_format;

  int video_index = -1;
  int audio_index = -1;

  AVStream *video_stream;
  AVStream *audio_stream;

  int i;

  for (i = 0; i < input_context->nb_streams && (video_index < 0 || audio_index < 0); i++) 
  {
    switch (input_context->streams[i]->codec->codec_type) {
      case CODEC_TYPE_VIDEO:
        video_index = i;
        input_context->streams[i]->discard = AVDISCARD_NONE;
        video_stream = add_output_stream(output_context, input_context->streams[i]);
        break;
      case CODEC_TYPE_AUDIO:
        audio_index = i;
        input_context->streams[i]->discard = AVDISCARD_NONE;
        audio_stream = add_output_stream(output_context, input_context->streams[i]);
        break;
      default:
        input_context->streams[i]->discard = AVDISCARD_ALL;
        break;
    }
  }

  if (av_set_parameters(output_context, NULL) < 0) 
  {
    fprintf(stderr, "Segmenter error: Invalid output format parameters\n");
    exit(1);
  }

  //dump_format(output_context, 0, config.filename_prefix, 1);

  if(video_index >= 0)
  {
    AVCodec *codec = avcodec_find_decoder(video_stream->codec->codec_id);
    if (!codec) 
    {
      fprintf(stderr, "Segmenter error: Could not find video decoder, key frames will not be honored\n");
    }

    if (avcodec_open(video_stream->codec, codec) < 0) 
    {
      fprintf(stderr, "Segmenter error: Could not open video decoder, key frames will not be honored\n");
    }
  }

  unsigned int output_index = 1;
  snprintf(output_filename, strlen(config.temp_directory) + 1 + strlen(config.filename_prefix) + 13, "%s/%s-%08u.ts", config.temp_directory, config.filename_prefix, output_index++);
  if (url_fopen(&output_context->pb, output_filename, URL_WRONLY) < 0) 
  {
    fprintf(stderr, "Segmenter error: Could not open '%s'\n", output_filename);
    exit(1);
  }

  if (av_write_header(output_context)) 
  {
    fprintf(stderr, "Segmenter error: Could not write mpegts header to first output file\n");
    exit(1);
  }

  unsigned int first_segment = 1;
  unsigned int last_segment = 0;

  double prev_segment_time = 0;
  double duration = 0;
  int decode_done;
  do 
  {
    double segment_time;
    AVPacket packet;

    decode_done = av_read_frame(input_context, &packet);
    if (decode_done < 0) 
    {
      break;
    }

    if (av_dup_packet(&packet) < 0) 
    {
      fprintf(stderr, "Segmenter error: Could not duplicate packet");
      av_free_packet(&packet);
      break;
    }

    /* Original Line. This meant.. split the segments ater a keyframe.
    But.. this ain't required and makes it impossible to have adaptive quality versions with
    different GOP size because A/V will get out of sync
    Ain't required you ask? Well.. the apple segmenter doesn't care about it. So why should we?
    if (packet.stream_index == video_index && (packet.flags & PKT_FLAG_KEY))
    */
    if (packet.stream_index == video_index) 
    {
      segment_time = (double)video_stream->pts.val * video_stream->time_base.num / video_stream->time_base.den;
    }
    // This stream is audioonly. No Video available
    else if (video_index < 0) 
    {
      segment_time = (double)audio_stream->pts.val * audio_stream->time_base.num / audio_stream->time_base.den;
    }
    else 
    {
      segment_time = prev_segment_time;
    }
    
    

    // done writing the current file?
    duration = (double) segment_time - prev_segment_time;
    //fprintf(stderr,"f Duration: %f\n", duration);
    
    if ((double) duration >= config.segment_length) 
    {
      // fprintf(stderr,"Duration: %f\n", duration);
      // if (output_context->duration != AV_NOPTS_VALUE) {
      //              int hours, mins, secs, us;
      //              secs = output_context->duration / AV_TIME_BASE;
      //              us = output_context->duration % AV_TIME_BASE;
      //              mins = secs / 60;
      //              secs %= 60;
      //              hours = mins / 60;
      //              mins %= 60;
      //              fprintf(stderr, "%02d:%02d:%02d.%02d", hours, mins, secs, (100 * us) / AV_TIME_BASE);
      //   } else {
      //              fprintf(stderr, "N/A");
        // }
        put_flush_packet(output_context->pb);
        url_fclose(output_context->pb);

      output_transfer_command(first_segment, ++last_segment, 0, config.encoding_profile, duration);

      snprintf(output_filename, strlen(config.temp_directory) + 1 + strlen(config.filename_prefix) + 13, "%s/%s-%08u.ts", config.temp_directory, config.filename_prefix, output_index++);
      if (url_fopen(&output_context->pb, output_filename, URL_WRONLY) < 0) 
      {
        fprintf(stderr, "Segmenter error: Could not open '%s'\n", output_filename);
        break;
      }

      prev_segment_time = segment_time;
    }
    // Don't use av_interleaved_write frame here. It will change the order of Audioframes.
    // This will not working if we're using multirate streaming. Audio Problems happen when
    // the player switches quality.
    ret = av_write_frame(output_context, &packet);
    if (ret < 0) 
    {
      fprintf(stderr, "Segmenter error: Could not write frame of stream: %d\n", ret);
    }
    else if (ret > 0) 
    {
      fprintf(stderr, "Segmenter info: End of stream requested\n");
      av_free_packet(&packet);
      break;
    }


    av_free_packet(&packet);
  } while (!decode_done);

  av_write_trailer(output_context);

  if (video_index >= 0) 
  {
    avcodec_close(video_stream->codec);
  }

  for(i = 0; i < output_context->nb_streams; i++) 
  {
    av_freep(&output_context->streams[i]->codec);
    av_freep(&output_context->streams[i]);
  }

  url_fclose(output_context->pb);
  av_free(output_context);

  output_transfer_command(first_segment, ++last_segment, 1, config.encoding_profile, duration);

  return 0;
}
