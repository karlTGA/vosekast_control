import React from 'react';
import { VosekastStore } from '../Store';
import { useStoreState } from 'pullstate';
import classNames from 'classnames';

export function FlowTag() {
  const flowState = useStoreState(VosekastStore, (s) => s.flowState);
  if (flowState == null) return <></>;

  const value = parseFloat(flowState.value).toFixed(2);
  return (
    <div
      className={classNames('info-tag', {
        'info-tag--success': flowState.stable,
        'info-tag--danger': !flowState.stable,
      })}
    >
      Volumeflow: {value} {flowState.unit}
    </div>
  );
}
