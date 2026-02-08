interface ImagePreviewProps {
  file: File;
}

export default function ImagePreview({ file }: ImagePreviewProps): JSX.Element {
  const imageUrl = URL.createObjectURL(file);

  return <img src={imageUrl} alt="preview" width={120} />;
}
