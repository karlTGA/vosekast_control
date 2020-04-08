import React from "react";
import { Button } from "antd";
import classNames from "classnames";

export function CommandButton({
  isActive,
  imagePath,
  title,
  onClick,
}: {
  isActive: boolean;
  imagePath: string;
  title: string;
  onClick: () => void;
}) {
  return (
    <Button
      className={classNames("device-command-button", {
        "device-deactivated": !isActive,
      })}
      onClick={onClick}
    >
      <img src={imagePath} alt="" />
      {title}
    </Button>
  );
}
