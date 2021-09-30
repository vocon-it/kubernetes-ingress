// +build aws

package main

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
	"math/big"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/marketplacemetering"
	"github.com/aws/aws-sdk-go-v2/service/marketplacemetering/types"

	"github.com/golang-jwt/jwt/v4"
)

var (
	productCode   string
	pubKeyVersion int32 = 1
	pubKeyString  string
)

func init() {
	startupCheckFn = checkAWSEntitlement
}

func checkAWSEntitlement() error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	nonce, err := generateRandomString(255)
	if err != nil {
		return err
	}

	cfg, err := config.LoadDefaultConfig(ctx)
	if err != nil {
		return fmt.Errorf("error loading AWS configuration: %w", err)
	}

	mpm := marketplacemetering.NewFromConfig(cfg)

	out, err := mpm.RegisterUsage(ctx, &marketplacemetering.RegisterUsageInput{ProductCode: &productCode, PublicKeyVersion: &pubKeyVersion, Nonce: &nonce})
	if err != nil {
		var notEnt *types.CustomerNotEntitledException
		var invRegion *types.InvalidRegionException
		var platNotSup *types.PlatformNotSupportedException
		if errors.As(err, &notEnt) {
			return fmt.Errorf("user not entitled, code: %v, message: %v, fault: %v", notEnt.ErrorCode(), notEnt.ErrorMessage(), notEnt.ErrorFault().String())
		}
		if errors.As(err, &invRegion) {
			return fmt.Errorf("invalid region, code: %v, message: %v, fault: %v", invRegion.ErrorCode(), invRegion.ErrorMessage(), invRegion.ErrorFault().String())
		}
		if errors.As(err, &platNotSup) {
			return fmt.Errorf("platform not supported, code: %v, message: %v, fault: %v", platNotSup.ErrorCode(), platNotSup.ErrorMessage(), platNotSup.ErrorFault().String())
		}
		return err
	}

	pk, err := base64.StdEncoding.DecodeString(pubKeyString)
	if err != nil {
		return fmt.Errorf("error decoding Public Key string: %w", err)
	}
	pubKey, err := jwt.ParseRSAPublicKeyFromPEM(pk)
	if err != nil {
		return fmt.Errorf("error parsing Public Key: %w", err)
	}

	token, err := jwt.ParseWithClaims(*out.Signature, &claims{}, KnownKeyfunc(jwt.SigningMethodPS256, pubKey))
	if err != nil {
		return fmt.Errorf("error parsing the JWT token: %w", err)
	}

	if claims, ok := token.Claims.(*claims); ok && token.Valid {
		if claims.ProductCode != productCode || claims.PublicKeyVersion != pubKeyVersion || claims.Nonce != nonce {
			return fmt.Errorf("the claims in the JWT token don't match the request")
		}
	} else {
		return fmt.Errorf("something is wrong with the JWT token")
	}

	return nil
}

func KnownKeyfunc(signingMethod jwt.SigningMethod, key interface{}) jwt.Keyfunc {
	return func(t *jwt.Token) (interface{}, error) {
		if signingMethod.Alg() != t.Header["alg"] {
			return nil, fmt.Errorf("unexpected signing method: %v, expected: %v", t.Header["alg"], signingMethod.Alg())
		}
		return key, nil
	}
}

type claims struct {
	ProductCode      string       `json:"productCode,omitempty"`
	PublicKeyVersion int32        `json:"publicKeyVersion,omitempty"`
	IssuedAt         *time.Time   `json:"iat,omitempty"`
	Nonce            string       `json:"nonce,omitempty"`
}

func (c *claims) VerifyNotBefore(nbf *time.Time, now time.Time, required bool) bool {
		if nbf == nil {
			return !required
		}
		return now.After(*nbf) || now.Equal(*nbf)
	}

func (c claims) Valid() error {
	if c.Nonce == "" {
		return jwt.NewValidationError("the JWT token doesn't include the Nonce", jwt.ValidationErrorClaimsInvalid)
	}
	if c.ProductCode == "" {
		return jwt.NewValidationError("the JWT token doesn't include the ProductCode", jwt.ValidationErrorClaimsInvalid)
	}
	if c.PublicKeyVersion == 0 {
		return jwt.NewValidationError("the JWT token doesn't include the PublicKeyVersion", jwt.ValidationErrorClaimsInvalid)
	}
	if !c.VerifyNotBefore(c.IssuedAt, time.Now(), false) {
		return jwt.NewValidationError("the JWT token is not valid yet", jwt.ValidationErrorNotValidYet)
	}

	return nil
}

func generateRandomString(n int) (string, error) {
	const letters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"
	ret := make([]byte, n)
	for i := 0; i < n; i++ {
		num, err := rand.Int(rand.Reader, big.NewInt(int64(len(letters))))
		if err != nil {
			return "", err
		}
		ret[i] = letters[num.Int64()]
	}

	return string(ret), nil
}
