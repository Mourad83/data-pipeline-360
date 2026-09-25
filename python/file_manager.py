import shutil


def copy_to_raw(file_path, raw_dir):

    raw_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = raw_dir / file_path.name

    shutil.copy2(
        file_path,
        destination
    )

    return destination


def save_to_processed(df, file_name, processed_dir):

    processed_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = processed_dir / file_name

    df.to_csv(
        destination,
        index=False,
        encoding="utf-8-sig"
    )

    return destination


def move_to_archive(file_path, archive_dir):

    archive_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = archive_dir / file_path.name

    shutil.move(
        str(file_path),
        str(destination)
    )

    return destination


def move_to_rejected(file_path, rejected_dir):

    rejected_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = rejected_dir / file_path.name

    shutil.move(
        str(file_path),
        str(destination)
    )

    return destination
