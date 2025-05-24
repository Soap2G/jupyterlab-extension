/*
 * Copyright European Organization for Nuclear Research (CERN)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * You may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Authors:
 * - Giovanni Guerrieri, <giovanni.guerrieri@cern.ch>, 2025
 */

import React from 'react';
import { createUseStyles } from 'react-jss';
import { TextField } from '../TextField';
import { IRucioOIDCAuth } from '../../types';
import { Spinning } from '../Spinning';

const useStyles = createUseStyles({
  container: {
    padding: '8px 16px 8px 16px'
  },
  label: {
    margin: '4px 0 4px 0'
  },
  textFieldContainer: {
    margin: '8px 0 8px 0'
  },
  warning: {
    margin: '8px 8px 16px 8px',
    color: 'var(--jp-ui-font-color2)',
    fontSize: '9pt'
  },
  loadingIcon: {
    fontSize: '10pt',
    verticalAlign: 'middle'
  },
  loadingContainer: {
    padding: '0 8px 0 8px',
    display: 'flex',
    alignItems: 'center'
  }
});

interface IOIDCAuthProps {
  params?: IRucioOIDCAuth;
  loading?: boolean;
  onAuthParamsChange: { (val: IRucioOIDCAuth): void };
}

type MyProps = IOIDCAuthProps & React.HTMLAttributes<HTMLDivElement>;

export const OIDCAuth: React.FC<MyProps> = ({
  params = { account: '' },
  loading,
  onAuthParamsChange
}) => {
  const classes = useStyles();

  const onAccountChange = (account?: string) => {
    onAuthParamsChange({ ...params, account });
  };

  const loadingSpinner = (
    <div className={classes.loadingContainer}>
      <Spinning className={`${classes.loadingIcon} material-icons`}>
        hourglass_top
      </Spinning>
    </div>
  );

  return (
    <>
      <div className={classes.container}>
        <div className={classes.textFieldContainer}>
          <div className={classes.label}>Account</div>
          <TextField
            placeholder="Account"
            value={params.account}
            onChange={e => onAccountChange(e.target.value)}
            disabled={loading}
            after={loading ? loadingSpinner : undefined}
          />
        </div>
      </div>
    </>
  );
};
