/* eslint-disable react/jsx-no-useless-fragment */
import React, { useEffect, useState } from "react";
import "./Button.scss"

export enum CopyButtonMode {
  Normal = "normal",
  Compact = "compact",
}

interface CopyButtonProps {
  text: string;
  mode?: CopyButtonMode;
  className?: string;
  hideText?: boolean
}

const CopyButton = ({ text, mode = CopyButtonMode.Normal, className = '', hideText = false }: CopyButtonProps) => {
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null;

    if (isCopied) {
      timeoutId = setTimeout(() => {
        setIsCopied(false);
      }, 2500);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [isCopied]);

  const handleCopyClick = () => {
    navigator.clipboard.writeText(text);
    setIsCopied(true);

    if (mode === CopyButtonMode.Compact) {
      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    }
  };

  const shouldWrapInTooltip = mode !== CopyButtonMode.Normal;
  const buttonContent = (
    <>
      {isCopied ? (
        <>
          {mode === CopyButtonMode.Normal && <span>copied</span>}
        </>
      ) : (
        <>
          {mode === CopyButtonMode.Normal && <span>{hideText ? '' : 'copy'}</span>}
        </>
      )}
    </>
  );
  return shouldWrapInTooltip ? (
      <button
        className={`chat-action-button lkb-opacity-70 lkb-text-gray-400 lkb-inline-flex lkb-items-center lkb-justify-center lkb-ml-auto lkb-gap-2 ${className}`}
        onClick={handleCopyClick}>
        {buttonContent}
      </button>
  ) : (
      <button
        className={`chat-action-button lkb-opacity-70 lkb-text-gray-400 lkb-inline-flex lkb-items-center lkb-justify-center lkb-ml-auto lkb-gap-2 ${className}`}
        onClick={handleCopyClick}>
        {buttonContent}
      </button>
  );
};

export default CopyButton;
