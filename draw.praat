# Combine the draw commands for Sound,
# Pitch and TextGrid objects

form Draw annotated Sound and Pitch...
  real left_Time_range_(s)        0
  real right_Time_range_(s)       0 (= all)
  real left_Vertical_range        0
  real right_Vertical_range       0 (= auto)
  real left_Frequency_range_(Hz)  0
  real right_Frequency_range_(Hz) 500
  optionmenu Sound_drawing_method: 1
    option Curve
    option Bars
    option Poles
    option Speckles
  boolean Show_boundaries yes
  boolean Use_text_styles yes
  boolean Garnish yes
  comment What proportion of the graph should be used for the Sound?
  positive Figure_ratio 0.5
endform

# Get information on current picture
info$ = Picture info
original_colour.r$ = extractWord$(info$,  "Red:")
original_colour.g$ = extractWord$(info$,  "Green:")
original_colour.b$ = extractWord$(info$,  "Blue:")
picture.line_width = extractNumber(info$, "Line width:")
picture.left       = extractNumber(info$, "Inner viewport left:")
picture.right      = extractNumber(info$, "Inner viewport right:")
picture.top        = extractNumber(info$, "Inner viewport top:")
picture.bottom     = extractNumber(info$, "Inner viewport bottom:")
picture.height     = picture.bottom - picture.top

# Sound options
sound.start   = left_Time_range
sound.end     = right_Time_range
sound.min     = left_Vertical_range
sound.max     = right_Vertical_range
sound.method$ = sound_drawing_method$
# Pitch options
pitch.min     = left_Frequency_range
pitch.max     = right_Frequency_range
pitch.created = 0

# Draw options
fzero.colour$      = "Cyan"
fzero.width        = 2
fzero.border       = 1
fzero.border_width = 2
point.marker_size  = 0.1
precision          = 3

# Identify objects
# If no Pitch object is selected, generate one
sound = selected("Sound")
textgrid = selected("TextGrid")
if numberOfSelected("Pitch")
  pitch = selected("Pitch")
else
  selectObject: sound
  pitch = To Pitch: 0,
    ... if !pitch.min then 75  else pitch.min fi,
    ... if !pitch.max then 600 else pitch.max fi
  pitch.created = 1
endif

# Identify ranges for sound
selectObject: sound
if !sound.start and !sound.end
  sound.start = Get start time
  sound.end = Get end time
endif
sound.duration = sound.end - sound.start
if !sound.min and !sound.max
  sound.min = Get minimum: sound.start, sound.end, "None"
  sound.max = Get maximum: sound.start, sound.end, "None"
endif

# Select top of figure, for Sound and Pitch data
Select inner viewport:
  ... picture.left,
  ... picture.right,
  ... picture.top,
  ... picture.top + (picture.height * figure_ratio)

# Draw sound
selectObject: sound
Draw: sound.start, sound.end, sound.min, sound.max, "no", sound.method$

# Garnish sound
if garnish
  Draw line: sound.start, sound.min, sound.end, sound.min
  if sound.min < 0 and sound.max > 0
    One mark left: 0, "yes", "yes", "no", ""
  endif
  One mark left: sound.min, "no", "yes", "no", fixed$(sound.min, precision)
  One mark left: sound.max, "no", "yes", "no", fixed$(sound.max, precision)
endif

# Extract range from TextGrid object
selectObject: textgrid
textgrid_part = Extract part: sound.start, sound.end, "yes"
total_tiers = Get number of tiers
tier.height = 1 / total_tiers

# Draw boundaries (on Sound and Pitch)
if show_boundaries
  for tier to total_tiers
    interval_tier = Is interval tier: tier
    item$ = if interval_tier then "interval" else "point" fi
    total_items = do("Get number of " + item$ + "s...", tier)
    for item to total_items
      if interval_tier
        time = Get end point: tier, item
      else
        time = Get time of point: tier, item
      endif
      One mark bottom: time, "no", "no", "yes", ""
  endfor
endif

# Draw pitch, above boundaries
selectObject: pitch
if fzero.border
  Line width: fzero.width + fzero.border_width
  White
  Draw: sound.start, sound.end, pitch.min, pitch.max, "no"
endif
Line width: fzero.width
Colour: fzero.colour$
Draw: sound.start, sound.end, pitch.min, pitch.max, "no"
Line width: 1

# Garnish pitch
if garnish
  One mark right: pitch.min, "yes", "yes", "no", ""
  One mark right: pitch.max, "no", "yes", "no", fixed$(pitch.max, 0)
  Text right: "yes", "Pitch (Hz)"
endif

# Return to original colour
Colour: "{" +
  ... original_colour.r$ + "," +
  ... original_colour.g$ + "," +
  ... original_colour.b$ + "}"

if 1 - figure_ratio
  # Select bottom of figure, for TextGrid data
  Select inner viewport:
    ... picture.left,
    ... picture.right,
    ... picture.top + (picture.height * figure_ratio),
    ... picture.bottom

  # Adjust vertical axis
  Axes: sound.start, sound.end, 1, 0

  # Draw TextGrid
  # A custom draw method is needed to ensure that the TextGrid is
  # drawn using only the part of the figure specified by the user
  selectObject: textgrid_part
  for tier to total_tiers
    tier.bottom = tier * tier.height
    tier.top = tier.bottom - tier.height
    tier.middle = tier.top + (tier.height / 2)
    if garnish and tier < total_tiers
      Draw line: sound.start, tier.bottom, sound.end, tier.bottom
    endif

    interval_tier = Is interval tier: tier
    item$ = if interval_tier then "interval" else "point" fi
    total_items = do("Get number of " + item$ + "s...", tier)
      for item to total_items
        if interval_tier
          time = Get end point: tier, item
          start = Get starting point: tier, item
          midpoint = start + ((time - start) / 2)
          if garnish
            Draw line: time, tier.bottom, time, tier.top
          endif
        else
          time = Get time of point: tier, item
          midpoint = time
          if garnish
            Draw line: time, tier.top, time, tier.top + tier.height * point.marker_size
            Draw line: time, tier.bottom, time, tier.bottom - tier.height * point.marker_size
          endif
        endif

        label$ = do$("Get label of " + item$ + "...", tier, item)
        if !use_text_styles
          label$ = replace$(label$, "\", "\bs", 0)
          label$ = replace_regex$(label$, "([%#^_])", "\\\1 ", 0)
        endif
        Text: midpoint, "Centre", tier.middle, "Half", label$
      endfor
  endfor
endif
removeObject: textgrid_part

# Select the full viewport
Select inner viewport:
  ... picture.left,
  ... picture.right,
  ... picture.top,
  ... picture.bottom

# Finish garnish
if garnish
  Draw inner box
  One mark bottom: sound.start, "no", "yes", "no", fixed$(sound.start, precision)
  One mark bottom: sound.end,   "no", "yes", "no", fixed$(sound.end,   precision)
  Text bottom: "yes", "Time (s)"
endif

# Re-select original objects
selectObject: sound, textgrid

# Remove Pitch object if it was created by us
# or add it to selection
if pitch.created
  nocheck removeObject: pitch
else
  plusObject: pitch
endif
