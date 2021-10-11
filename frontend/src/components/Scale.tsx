import React from 'react';
import { VosekastStore } from '../Store';
import { useStoreState } from 'pullstate';
import classNames from 'classnames';

export function ScaleTag() {
  const scaleState = useStoreState(VosekastStore, (s) => s.scaleState);
  if (scaleState == null) return <></>;

  const value = parseFloat(scaleState.value).toFixed(2);
  return (
    <div
      className={classNames('info-tag', {
        'info-tag--success': scaleState.stable,
        'info-tag--danger': !scaleState.stable,
      })}
    >
      Scale: {value} {scaleState.unit}
    </div>
  );
}
