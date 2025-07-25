import genanki
import json
import os
import sys
import shutil
import generators.gen_utils as utils

def gen_verbs(json_file, deck_name, apkg_filename='Finnish_Verbs.apkg'):

    """
    Making card structure that contains ver conjugations with images and audio
    Question: Base verb and Image
    {{Verb}} - {{Question}}{{#Image}}<br><hr>{{Image}}<br>{{/Image}}
    Answer: Conjugated form
    <table>
    <tr>
    <td>{{Verb1}}</td>
    <td>{{Audio1}}</td>
    </tr>
    ...
    </table>
    """

    # Create the model for the Anki cards
    model_id = 1234567890
    model = genanki.Model(
        model_id,
        'Verb Conjugation Table with Image and Audio',
        fields=[
            {'name': 'Question'},
            {'name': 'Image'},
            {'name': 'Note'},
            {'name': 'Verb1'},
            {'name': 'Translate1'},
            {'name': 'Audio1'},
            {'name': 'Verb2'},
            {'name': 'Translate2'},
            {'name': 'Audio2'},
            {'name': 'Verb3'},
            {'name': 'Translate3'},
            {'name': 'Audio3'},
            {'name': 'Verb4'},
            {'name': 'Translate4'},
            {'name': 'Audio4'},
            {'name': 'Verb5'},
            {'name': 'Translate5'},
            {'name': 'Audio5'},
            {'name': 'Verb6'},
            {'name': 'Translate6'},
            {'name': 'Audio6'},
        ],
        templates=[
            {
                'name': 'Verb Conjugation Card',
                'qfmt': '{{Question}}{{#Image}}<br><hr>{{Image}}<br>{{/Image}}',
                'afmt': """
                {{FrontSide}}<br><hr>
                <table>
                <tr><td>{{Verb1}}</td><td> ({{Translate1}})</td><td>{{Audio1}}</td></tr>
                <tr><td>{{Verb2}}</td><td> ({{Translate2}})</td><td>{{Audio2}}</td></tr>
                <tr><td>{{Verb3}}</td><td> ({{Translate3}})</td><td>{{Audio3}}</td></tr>
                <tr><td>{{Verb4}}</td><td> ({{Translate4}})</td><td>{{Audio4}}</td></tr>
                <tr><td>{{Verb5}}</td><td> ({{Translate5}})</td><td>{{Audio5}}</td></tr>
                <tr><td>{{Verb6}}</td><td> ({{Translate6}})</td><td>{{Audio6}}</td></tr>
                </table>
                {{Note}}
            """,
            },
        ],
    )

    # Create the deck
    deck_id = 987654321
    deck = genanki.Deck(
        deck_id,
        deck_name,
    )

    # Load data from the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        verbs = json.load(f)

    # Directory for media files (audio and images)
    if os.path.exists('media'):
        shutil.rmtree('media')
    media_folder = 'media'
    os.makedirs(media_folder, exist_ok=True)

    # List to store paths to media files
    media_files = []

    # Add cards to the deck
    for verb_data in verbs:
        verb = verb_data['verb']
        question = f"Conjugate the verb '{verb}'"
        sanitized_image_filename = ""

        # Handle optional image
        if 'image' in verb_data:
            image_url = verb_data['image']
            if len(image_url):
                sanitized_image_filename = os.path.basename(image_url)
                image_path = os.path.join(media_folder, sanitized_image_filename)
                utils.download_image(image_url, image_path)
                media_files.append(image_path)

        # Generate conjugations and audio
        conjugations = verb_data['conjugations']
        translations = verb_data['translations']
        conjugation_fields = []
        for i, conjugation in enumerate(conjugations):
            translate = translations[i]
            sanitized_audio_filename = utils.sanitize_filename(f"{verb}_conjugation_{i + 1}.mp3")
            audio_path = os.path.join(media_folder, sanitized_audio_filename)
            utils.generate_audio(conjugation, audio_path)
            media_files.append(audio_path)
            conjugation_fields.extend([conjugation, translate, f"[sound:{sanitized_audio_filename}]"])

        # Fill missing fields if there are fewer than 6 conjugations
        while len(conjugation_fields) < 6 * 3:
            conjugation_fields.extend(["", ""])

        note_field = ""
        if 'note' in verb_data:
            note_field = verb_data['note']
        # Add note
        note = genanki.Note(
            model=model,
            fields=[
                question,                   # Question
                f'<img src="{sanitized_image_filename}"/>' if len(sanitized_image_filename) > 0 else "",   # Image
                *conjugation_fields,        # Conjugations and audio
                note_field,                 # Note
            ],
        )
        deck.add_note(note)

    # Create the package and include media files
    package = genanki.Package(deck)
    package.media_files = media_files  # Add media files (audio + images) to the package
    package.write_to_file(apkg_filename)

    return True


if __name__ == '__main__':
    sys.exit(1)