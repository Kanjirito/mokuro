from pathlib import Path

import fire
from loguru import logger
from natsort import natsorted

from mokuro import OverlayGenerator


def run(*paths,
        parent_dir=None,
        pretrained_model_name_or_path='kha-white/manga-ocr-base',
        force_cpu=False,
        as_one_file=True,
        disable_confirmation=False,
        disable_ocr=False,
        right_to_left=True,
        double_page_view=True,
        has_cover=False,
        ctrl_to_pan=False,
        display_ocr=True,
        textbox_borders=False,
        editable_text=False,
        eink_mode=False,
        textbox_click_toggle=False,
        ):
    """
    Process manga volumes with mokuro.

    Args:
        path(s): Paths to manga volumes
        parent_dir: Parent directory to scan for volumes. If provided, all volumes inside this directory will be processed.
        pretrained_model_name_or_path: Name or path of the manga-ocr model.
        force_cpu: Force the use of CPU even if CUDA is available.
        as_one_file: If False, generate separate CSS and JS files instead of embedding them in the HTML file.
        disable_confirmation: Disable confirmation prompt. If False,the user will be prompted to confirm the list of volumes to be processed.
        disable_ocr: Disable OCR processing. Generate files without OCR results.
        right_to_left: Toggle the reader default for right to left reading.
        double_page_view: Toggle the reader default for double page view.
        has_cover: Toggle the reader default for "first page is cover"
        ctrl_to_pan: Toggle the reader default for Ctrl+Mouse to pan.
        display_ocr: Toggle the reader default for OCR text display.
        textbox_borders: Toggle the reader default for OCR text box border display.
        editable_text: Toggle the reader default for editable text.
        eink_mode: Toggle the reader default for e-ink mode.
        textbox_click_toggle: Toggle the reader default for text box visibility toggling.
    """

    default_state = {
        'page_idx': 0,
        'page2_idx': -1,
        'defaultZoomMode': 'fit to screen',
        'r2l': right_to_left,
        'doublePageView': double_page_view,
        'hasCover': has_cover,
        'ctrlToPan': ctrl_to_pan,
        'displayOCR': display_ocr,
        'textBoxBorders': textbox_borders,
        'editableText': editable_text,
        'fontSize': 'auto',
        'eInkMode': eink_mode,
        'toggleOCRTextBoxes': textbox_click_toggle,
        'backgroundColor': '#C4C3D0',
    }
    
    if disable_ocr:
        logger.info('Running with OCR disabled')

    paths = [Path(p).expanduser().absolute() for p in paths]

    if parent_dir is not None:
        for p in Path(parent_dir).expanduser().absolute().iterdir():
            if p.is_dir() and p.stem != '_ocr' and p not in paths:
                paths.append(p)

    if len(paths) == 0:
        logger.error('Found no paths to process. Did you set the paths correctly?')
        return

    paths = natsorted(paths)

    print(f'\nPaths to process:\n')
    for p in paths:
        print(p)

    if not disable_confirmation:
        inp = input('\nEach of the paths above will be treated as one volume. Continue? [yes/no]\n')
        if inp.lower() not in ('y', 'yes'):
            return

    ovg = OverlayGenerator(
        default_state,
        pretrained_model_name_or_path=pretrained_model_name_or_path,
        force_cpu=force_cpu,
        disable_ocr=disable_ocr
    )

    num_sucessful = 0
    for i, path in enumerate(paths):
        logger.info(f'Processing {i + 1}/{len(paths)}: {path}')
        try:
            ovg.process_dir(path, as_one_file=as_one_file)
        except Exception:
            logger.exception(f'Error while processing {path}')
        else:
            num_sucessful += 1

    logger.info(f'Processed successfully: {num_sucessful}/{len(paths)}')


if __name__ == '__main__':
    fire.Fire(run)
